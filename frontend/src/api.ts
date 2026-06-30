export type UserRole = 'user' | 'manager' | 'admin'
export type TaskStatus = 'open' | 'in_progress' | 'done'

export type User = {
  id: number
  email: string
  is_active: boolean
  role: UserRole
  created_at: string
  team_id: number | null
}

export type Team = {
  id: number
  name: string
  created_at: string
}

export type TeamWithJoinCode = Team & {
  join_code: string
}

export type TeamJoinCode = {
  join_code: string
}

export type TeamWithMembers = Team & {
  users: User[]
}

export type Task = {
  id: number
  title: string
  description: string | null
  status: TaskStatus
  deadline: string | null
  creator_id: number
  assignee_id: number | null
  team_id: number
  created_at: string
}

export type Meeting = {
  id: number
  title: string
  description: string | null
  starts_at: string
  ends_at: string
  creator_id: number
  participant_id: number
  team_id: number
  is_cancelled: boolean
  created_at: string
}

export type CalendarRead = {
  tasks: Task[]
  meetings: Meeting[]
}

export type EvaluationAverage = {
  average_score: number | null
  evaluations_count: number
}

export type TaskComment = {
  id: number
  task_id: number
  author_id: number
  text: string
  created_at: string
}

export class ApiError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

type RequestOptions = {
  token?: string | null
  method?: string
  body?: unknown
  form?: URLSearchParams
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const headers = new Headers()

  if (options.token) {
    headers.set('Authorization', `Bearer ${options.token}`)
  }

  let body: BodyInit | undefined
  if (options.form) {
    body = options.form
    headers.set('Content-Type', 'application/x-www-form-urlencoded')
  } else if (options.body !== undefined) {
    body = JSON.stringify(options.body)
    headers.set('Content-Type', 'application/json')
  }

  const response = await fetch(`/api/v1${path}`, {
    method: options.method ?? 'GET',
    headers,
    body,
  })

  if (response.status === 204) {
    return undefined as T
  }

  const contentType = response.headers.get('content-type')
  const data = contentType?.includes('application/json')
    ? await response.json()
    : null

  if (!response.ok) {
    const detail = data?.detail
    const message =
      typeof detail === 'string'
        ? detail
        : Array.isArray(detail)
          ? 'Проверьте заполнение полей.'
          : 'Запрос не выполнен.'
    throw new ApiError(response.status, message)
  }

  return data as T
}

export const api = {
  login(email: string, password: string) {
    const form = new URLSearchParams()
    form.set('username', email)
    form.set('password', password)
    return request<{ access_token: string; token_type: string }>('/auth/login', {
      method: 'POST',
      form,
    })
  },

  register(email: string, password: string) {
    return request<User>('/users', {
      method: 'POST',
      body: { email, password },
    })
  },

  me(token: string) {
    return request<User>('/users/me', { token })
  },

  updateMe(token: string, payload: { email?: string; password?: string }) {
    return request<User>('/users/me', {
      token,
      method: 'PATCH',
      body: payload,
    })
  },

  deactivateMe(token: string) {
    return request<User>('/users/me', {
      token,
      method: 'DELETE',
    })
  },

  listTasks(token: string) {
    return request<Task[]>('/tasks', { token })
  },

  createTask(
    token: string,
    payload: {
      title: string
      description?: string | null
      deadline?: string | null
      assignee_id?: number | null
    },
  ) {
    return request<Task>('/tasks', {
      token,
      method: 'POST',
      body: payload,
    })
  },

  updateTask(token: string, taskId: number, payload: Partial<Task>) {
    return request<Task>(`/tasks/${taskId}`, {
      token,
      method: 'PATCH',
      body: payload,
    })
  },

  deleteTask(token: string, taskId: number) {
    return request<void>(`/tasks/${taskId}`, {
      token,
      method: 'DELETE',
    })
  },

  listTaskComments(token: string, taskId: number) {
    return request<TaskComment[]>(`/tasks/${taskId}/comments`, { token })
  },

  createTaskComment(token: string, taskId: number, text: string) {
    return request<TaskComment>(`/tasks/${taskId}/comments`, {
      token,
      method: 'POST',
      body: { text },
    })
  },

  deleteTaskComment(token: string, taskId: number, commentId: number) {
    return request<void>(`/tasks/${taskId}/comments/${commentId}`, {
      token,
      method: 'DELETE',
    })
  },

  createEvaluation(token: string, taskId: number, score: number) {
    return request(`/evaluations/tasks/${taskId}`, {
      token,
      method: 'POST',
      body: { score },
    })
  },

  getAverageEvaluation(token: string) {
    return request<EvaluationAverage>('/evaluations/me/average', { token })
  },

  getMyTeam(token: string) {
    return request<TeamWithMembers>('/teams/me', { token })
  },

  getMyTeamJoinCode(token: string) {
    return request<TeamJoinCode>('/teams/me/join-code', { token })
  },

  createTeam(token: string, name: string) {
    return request<TeamWithJoinCode>('/teams', {
      token,
      method: 'POST',
      body: { name },
    })
  },

  joinTeam(token: string, joinCode: string) {
    return request<User>('/teams/join', {
      token,
      method: 'POST',
      body: { join_code: joinCode },
    })
  },

  updateMemberRole(token: string, memberId: number, role: UserRole) {
    return request<User>(`/teams/members/${memberId}/role`, {
      token,
      method: 'PATCH',
      body: { role },
    })
  },

  removeMember(token: string, memberId: number) {
    return request<void>(`/teams/members/${memberId}`, {
      token,
      method: 'DELETE',
    })
  },

  listMeetings(token: string) {
    return request<Meeting[]>('/meetings', { token })
  },

  createMeeting(
    token: string,
    payload: {
      title: string
      description?: string | null
      starts_at: string
      ends_at: string
      participant_id: number
    },
  ) {
    return request<Meeting>('/meetings', {
      token,
      method: 'POST',
      body: payload,
    })
  },

  cancelMeeting(token: string, meetingId: number) {
    return request<Meeting>(`/meetings/${meetingId}/cancel`, {
      token,
      method: 'PATCH',
    })
  },

  getCalendar(token: string, startsAt: string, endsAt: string) {
    const params = new URLSearchParams({ starts_at: startsAt, ends_at: endsAt })
    return request<CalendarRead>(`/calendar?${params.toString()}`, { token })
  },
}
