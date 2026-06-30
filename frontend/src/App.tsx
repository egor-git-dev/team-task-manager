import {
  CalendarDays,
  CheckCircle2,
  ClipboardList,
  LogOut,
  RefreshCcw,
  Save,
  Shield,
  Star,
  Trash2,
  UserCircle,
  Users,
} from 'lucide-react'
import {
  type FormEvent,
  type ReactNode,
  useCallback,
  useEffect,
  useMemo,
  useState,
} from 'react'
import './App.css'
import { ApiError, api } from './api'
import type {
  CalendarRead,
  EvaluationAverage,
  Meeting,
  Task,
  TaskComment,
  TaskStatus,
  TeamWithMembers,
  User,
  UserRole,
} from './api'

type View = 'overview' | 'tasks' | 'team' | 'calendar' | 'profile'

const tokenKey = 'team-task-manager-token'

function formatDate(value: string | null | undefined) {
  if (!value) return 'Дата не указана'
  return new Intl.DateTimeFormat('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(value))
}

function roleLabel(role: UserRole) {
  const labels: Record<UserRole, string> = {
    user: 'Сотрудник',
    manager: 'Менеджер',
    admin: 'Администратор',
  }
  return labels[role]
}

function statusLabel(status: TaskStatus) {
  const labels: Record<TaskStatus, string> = {
    open: 'Открыта',
    in_progress: 'В работе',
    done: 'Готово',
  }
  return labels[status]
}

function memberLabel(member: User) {
  return `${member.email} · ${roleLabel(member.role)}`
}

function getErrorMessage(error: unknown, fallback: string) {
  if (!(error instanceof Error)) return fallback

  const messages: Record<string, string> = {
    'Could not validate credentials': 'Не удалось подтвердить вход. Войдите заново.',
    'Incorrect email or password': 'Неверный email или пароль.',
    'Email already registered': 'Пользователь с таким email уже зарегистрирован.',
    'User is inactive': 'Аккаунт отключён.',
    'User is not in a team': 'Сначала нужно вступить в команду.',
    'Task not found': 'Задача не найдена.',
    'Comment not found': 'Комментарий не найден.',
    'Permission denied': 'Недостаточно прав для этого действия.',
    'Team not found': 'Команда не найдена.',
    'Join code not found': 'Команда с таким кодом не найдена.',
    'Meeting overlaps': 'В это время уже есть встреча.',
  }

  return messages[error.message] ?? error.message ?? fallback
}

function toApiDateTime(value: string) {
  return value ? new Date(value).toISOString() : null
}

function toInputDateTime(date: Date) {
  const offsetMs = date.getTimezoneOffset() * 60_000
  return new Date(date.getTime() - offsetMs).toISOString().slice(0, 16)
}

function addDays(date: Date, days: number) {
  const copy = new Date(date)
  copy.setDate(copy.getDate() + days)
  return copy
}

function emptyTaskForm() {
  return {
    title: '',
    description: '',
    deadline: '',
    assigneeId: '',
  }
}

function emptyMeetingForm() {
  const start = addDays(new Date(), 1)
  start.setMinutes(0, 0, 0)
  const end = new Date(start)
  end.setHours(end.getHours() + 1)
  return {
    title: '',
    description: '',
    startsAt: toInputDateTime(start),
    endsAt: toInputDateTime(end),
    participantId: '',
  }
}

function App() {
  const [token, setToken] = useState(() => localStorage.getItem(tokenKey))
  const [user, setUser] = useState<User | null>(null)
  const [view, setView] = useState<View>('overview')
  const [message, setMessage] = useState<string | null>(null)
  const [loadingUser, setLoadingUser] = useState(Boolean(token))

  useEffect(() => {
    if (!token) {
      setUser(null)
      setLoadingUser(false)
      return
    }

    setLoadingUser(true)
    api
      .me(token)
      .then(setUser)
      .catch(() => {
        localStorage.removeItem(tokenKey)
        setToken(null)
        setUser(null)
      })
      .finally(() => setLoadingUser(false))
  }, [token])

  function handleToken(nextToken: string) {
    localStorage.setItem(tokenKey, nextToken)
    setToken(nextToken)
  }

  function logout() {
    localStorage.removeItem(tokenKey)
    setToken(null)
    setUser(null)
    setView('overview')
  }

  const notify = useCallback((text: string) => {
    setMessage(text)
    window.setTimeout(() => setMessage(null), 3800)
  }, [])

  if (loadingUser) {
    return (
      <main className="loading-screen">
        <RefreshCcw className="spin" size={28} />
      </main>
    )
  }

  if (!token || !user) {
    return <AuthScreen onToken={handleToken} />
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">TT</div>
          <div>
            <strong>Менеджер задач</strong>
            <span>рабочее пространство команды</span>
          </div>
        </div>

        <nav className="nav-list" aria-label="Основная навигация">
          <NavButton
            icon={<ClipboardList size={18} />}
            active={view === 'overview'}
            onClick={() => setView('overview')}
          >
            Обзор
          </NavButton>
          <NavButton
            icon={<CheckCircle2 size={18} />}
            active={view === 'tasks'}
            onClick={() => setView('tasks')}
          >
            Задачи
          </NavButton>
          <NavButton
            icon={<Users size={18} />}
            active={view === 'team'}
            onClick={() => setView('team')}
          >
            Команда
          </NavButton>
          <NavButton
            icon={<CalendarDays size={18} />}
            active={view === 'calendar'}
            onClick={() => setView('calendar')}
          >
            Календарь
          </NavButton>
          <NavButton
            icon={<UserCircle size={18} />}
            active={view === 'profile'}
            onClick={() => setView('profile')}
          >
            Профиль
          </NavButton>
        </nav>
      </aside>

      <main className="workspace">
        <header className="topbar">
          <div>
            <h1>{titleForView(view)}</h1>
          </div>
          <div className="session-panel">
            <div className="session-user">
              <span className="eyebrow">Вы вошли как</span>
              <strong>{user.email}</strong>
              <span>{roleLabel(user.role)}</span>
            </div>
            <button className="icon-button" type="button" onClick={logout} title="Выйти">
              <LogOut size={18} />
            </button>
          </div>
        </header>

        {message ? <div className="toast">{message}</div> : null}

        {view === 'overview' ? (
          <Overview token={token} user={user} onNavigate={setView} />
        ) : null}
        {view === 'tasks' ? <TasksPage token={token} user={user} notify={notify} /> : null}
        {view === 'team' ? (
          <TeamPage token={token} user={user} onUserChange={setUser} notify={notify} />
        ) : null}
        {view === 'calendar' ? <CalendarPage token={token} notify={notify} /> : null}
        {view === 'profile' ? (
          <ProfilePage token={token} user={user} onUserChange={setUser} logout={logout} notify={notify} />
        ) : null}
      </main>
    </div>
  )
}

function titleForView(view: View) {
  const titles: Record<View, string> = {
    overview: 'Обзор',
    tasks: 'Задачи',
    team: 'Команда',
    calendar: 'Календарь',
    profile: 'Профиль',
  }
  return titles[view]
}

function NavButton({
  active,
  children,
  icon,
  onClick,
}: {
  active: boolean
  children: string
  icon: ReactNode
  onClick: () => void
}) {
  return (
    <button className={`nav-button ${active ? 'active' : ''}`} type="button" onClick={onClick}>
      {icon}
      <span>{children}</span>
    </button>
  )
}

function AuthScreen({ onToken }: { onToken: (token: string) => void }) {
  const [mode, setMode] = useState<'login' | 'register'>('login')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  async function submit(event: FormEvent) {
    event.preventDefault()
    setError(null)
    setSubmitting(true)

    try {
      if (mode === 'register') {
        await api.register(email, password)
      }
      const token = await api.login(email, password)
      onToken(token.access_token)
    } catch (error) {
      setError(getErrorMessage(error, 'Не удалось войти. Проверьте данные.'))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <main className="auth-screen">
      <section className="auth-panel">
        <div className="auth-copy">
          <div className="brand inline">
            <div className="brand-mark">TT</div>
            <div>
              <strong>Менеджер задач</strong>
              <span>командная работа без лишнего шума</span>
            </div>
          </div>
          <h1>Задачи, встречи и команда в одном понятном интерфейсе.</h1>
          <p>
            Войдите в аккаунт или создайте новый. После входа можно управлять
            задачами, командой, календарём и профилем.
          </p>
        </div>

        <form className="auth-form" onSubmit={submit}>
          <div className="segmented" role="tablist" aria-label="Режим входа">
            <button
              type="button"
              className={mode === 'login' ? 'selected' : ''}
              onClick={() => setMode('login')}
            >
              Вход
            </button>
            <button
              type="button"
              className={mode === 'register' ? 'selected' : ''}
              onClick={() => setMode('register')}
            >
              Регистрация
            </button>
          </div>

          <label>
            Email
            <input
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
              autoComplete="email"
            />
          </label>
          <label>
            Пароль
            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
              minLength={8}
              autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
            />
          </label>

          {error ? <p className="form-error">{error}</p> : null}

          <button className="primary-button" type="submit" disabled={submitting}>
            {submitting
              ? 'Подождите...'
              : mode === 'login'
                ? 'Войти'
                : 'Создать аккаунт'}
          </button>
        </form>
      </section>
    </main>
  )
}

function Overview({
  onNavigate,
  token,
  user,
}: {
  onNavigate: (view: View) => void
  token: string
  user: User
}) {
  const [tasks, setTasks] = useState<Task[]>([])
  const [meetings, setMeetings] = useState<Meeting[]>([])
  const [average, setAverage] = useState<EvaluationAverage | null>(null)

  useEffect(() => {
    Promise.allSettled([
      api.listTasks(token),
      api.listMeetings(token),
      api.getAverageEvaluation(token),
    ]).then(([tasksResult, meetingsResult, averageResult]) => {
      if (tasksResult.status === 'fulfilled') setTasks(tasksResult.value)
      if (meetingsResult.status === 'fulfilled') setMeetings(meetingsResult.value)
      if (averageResult.status === 'fulfilled') setAverage(averageResult.value)
    })
  }, [token])

  const openTasks = tasks.filter((task) => task.status !== 'done').length
  const doneTasks = tasks.filter((task) => task.status === 'done').length

  return (
    <section className="view-grid">
      <div className="summary-grid">
        <SummaryItem label="Открытые задачи" value={openTasks} />
        <SummaryItem label="Готовые задачи" value={doneTasks} />
        <SummaryItem label="Встречи" value={meetings.length} />
        <SummaryItem
          label="Средняя оценка"
          value={average?.average_score?.toFixed(1) ?? '—'}
        />
      </div>

      <section className="panel">
        <div className="panel-heading">
          <div>
            <h2>Аккаунт</h2>
            <p>Ваши права и привязка к команде.</p>
          </div>
          <Shield size={20} />
        </div>
        <dl className="detail-list">
          <div>
            <dt>Email</dt>
            <dd>{user.email}</dd>
          </div>
          <div>
            <dt>Роль</dt>
            <dd>{roleLabel(user.role)}</dd>
          </div>
          <div>
            <dt>Команда</dt>
            <dd>{user.team_id ?? 'Нет команды'}</dd>
          </div>
        </dl>
      </section>

      <section className="panel">
        <div className="panel-heading">
          <div>
            <h2>Ближайшая работа</h2>
            <p>Задачи, которые видны вашему аккаунту.</p>
          </div>
          <button className="text-button" type="button" onClick={() => onNavigate('tasks')}>
            Открыть задачи
          </button>
        </div>
        <TaskTable tasks={tasks.slice(0, 5)} compact />
      </section>
    </section>
  )
}

function SummaryItem({ label, value }: { label: string; value: number | string }) {
  return (
    <div className="summary-item">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  )
}

function TasksPage({
  notify,
  token,
  user,
}: {
  notify: (message: string) => void
  token: string
  user: User
}) {
  const [tasks, setTasks] = useState<Task[]>([])
  const [members, setMembers] = useState<User[]>([])
  const [form, setForm] = useState(emptyTaskForm)
  const [selectedTask, setSelectedTask] = useState<Task | null>(null)
  const [comments, setComments] = useState<TaskComment[]>([])
  const [commentText, setCommentText] = useState('')
  const [loadingComments, setLoadingComments] = useState(false)
  const [loading, setLoading] = useState(true)
  const canCreate = user.role === 'manager' || user.role === 'admin'

  const loadTasks = useCallback(async () => {
    setLoading(true)
    try {
      setTasks(await api.listTasks(token))
    } catch (error) {
      notify(getErrorMessage(error, 'Не удалось загрузить задачи.'))
    } finally {
      setLoading(false)
    }
  }, [notify, token])

  const loadTeamMembers = useCallback(async () => {
    try {
      const team = await api.getMyTeam(token)
      setMembers(team.users)
    } catch {
      setMembers([])
    }
  }, [token])

  useEffect(() => {
    void loadTasks()
    void loadTeamMembers()
  }, [loadTasks, loadTeamMembers])

  async function createTask(event: FormEvent) {
    event.preventDefault()
    try {
      await api.createTask(token, {
        title: form.title,
        description: form.description || null,
        deadline: toApiDateTime(form.deadline),
        assignee_id: form.assigneeId ? Number(form.assigneeId) : null,
      })
      setForm(emptyTaskForm())
      notify('Задача создана.')
      await loadTasks()
    } catch (error) {
      notify(getErrorMessage(error, 'Не удалось создать задачу.'))
    }
  }

  async function updateStatus(task: Task, status: TaskStatus) {
    try {
      await api.updateTask(token, task.id, { status })
      await loadTasks()
    } catch (error) {
      notify(getErrorMessage(error, 'Не удалось обновить задачу.'))
    }
  }

  async function updateAssignee(task: Task, assigneeId: number | null) {
    try {
      await api.updateTask(token, task.id, { assignee_id: assigneeId })
      notify(assigneeId ? 'Исполнитель назначен.' : 'Исполнитель снят.')
      await loadTasks()
    } catch (error) {
      notify(getErrorMessage(error, 'Не удалось изменить исполнителя.'))
    }
  }

  async function openComments(task: Task) {
    if (selectedTask?.id === task.id) {
      setSelectedTask(null)
      setComments([])
      setCommentText('')
      return
    }

    setSelectedTask(task)
    setCommentText('')
    setLoadingComments(true)
    try {
      setComments(await api.listTaskComments(token, task.id))
    } catch (error) {
      notify(getErrorMessage(error, 'Не удалось загрузить комментарии.'))
    } finally {
      setLoadingComments(false)
    }
  }

  async function reloadComments(taskId: number) {
    setLoadingComments(true)
    try {
      setComments(await api.listTaskComments(token, taskId))
    } catch (error) {
      notify(getErrorMessage(error, 'Не удалось загрузить комментарии.'))
    } finally {
      setLoadingComments(false)
    }
  }

  async function createComment(event: FormEvent) {
    event.preventDefault()
    if (!selectedTask || !commentText.trim()) return

    try {
      await api.createTaskComment(token, selectedTask.id, commentText.trim())
      setCommentText('')
      await reloadComments(selectedTask.id)
    } catch (error) {
      notify(getErrorMessage(error, 'Не удалось добавить комментарий.'))
    }
  }

  async function deleteComment(comment: TaskComment) {
    if (!selectedTask) return

    try {
      await api.deleteTaskComment(token, selectedTask.id, comment.id)
      await reloadComments(selectedTask.id)
    } catch (error) {
      notify(getErrorMessage(error, 'Не удалось удалить комментарий.'))
    }
  }

  async function deleteTask(task: Task) {
    try {
      await api.deleteTask(token, task.id)
      if (selectedTask?.id === task.id) {
        setSelectedTask(null)
        setComments([])
      }
      notify('Задача удалена.')
      await loadTasks()
    } catch (error) {
      notify(getErrorMessage(error, 'Не удалось удалить задачу.'))
    }
  }

  async function evaluateTask(task: Task, score: number) {
    try {
      await api.createEvaluation(token, task.id, score)
      notify('Оценка сохранена.')
    } catch (error) {
      notify(getErrorMessage(error, 'Не удалось поставить оценку.'))
    }
  }

  return (
    <section className="view-grid">
      {canCreate ? (
        <form className="panel form-grid" onSubmit={createTask}>
          <div className="panel-heading full">
            <div>
              <h2>Создать задачу</h2>
              <p>Менеджеры и администраторы могут назначать задачи участникам команды.</p>
            </div>
          </div>
          <label>
            Название
            <input
              value={form.title}
              onChange={(event) => setForm({ ...form, title: event.target.value })}
              required
            />
          </label>
          <label>
            Исполнитель
            <select
              value={form.assigneeId}
              onChange={(event) => setForm({ ...form, assigneeId: event.target.value })}
            >
              <option value="">Без исполнителя</option>
              {members.map((member) => (
                <option key={member.id} value={member.id}>
                  {memberLabel(member)}
                </option>
              ))}
            </select>
          </label>
          <label>
            Дедлайн
            <input
              type="datetime-local"
              value={form.deadline}
              onChange={(event) => setForm({ ...form, deadline: event.target.value })}
            />
          </label>
          <label className="full">
            Описание
            <textarea
              value={form.description}
              onChange={(event) => setForm({ ...form, description: event.target.value })}
              rows={3}
            />
          </label>
          <button className="primary-button" type="submit">
            Создать задачу
          </button>
        </form>
      ) : null}

      <section className="panel">
        <div className="panel-heading">
          <div>
            <h2>Задачи</h2>
            <p>{loading ? 'Загружаем задачи...' : `Найдено задач: ${tasks.length}`}</p>
          </div>
          <button className="icon-button" type="button" onClick={loadTasks} title="Обновить">
            <RefreshCcw size={18} />
          </button>
        </div>
        <TaskTable
          members={members}
          selectedTaskId={selectedTask?.id ?? null}
          tasks={tasks}
          onAssigneeChange={canCreate ? updateAssignee : undefined}
          onCommentsOpen={openComments}
          onDelete={deleteTask}
          onEvaluate={canCreate ? evaluateTask : undefined}
          onStatusChange={updateStatus}
        />
        {selectedTask ? (
          <div className="comments-panel">
            <div className="panel-heading">
              <div>
                <h2>Комментарии</h2>
                <p>{selectedTask.title}</p>
              </div>
              <button
                className="icon-button"
                type="button"
                onClick={() => reloadComments(selectedTask.id)}
                title="Обновить"
              >
                <RefreshCcw size={18} />
              </button>
            </div>

            <form className="comment-form" onSubmit={createComment}>
              <textarea
                value={commentText}
                onChange={(event) => setCommentText(event.target.value)}
                placeholder="Напишите комментарий"
                rows={3}
                required
              />
              <button className="primary-button" type="submit">
                Добавить
              </button>
            </form>

            <div className="comment-list">
              {loadingComments ? (
                <p className="empty-state">Загружаем комментарии...</p>
              ) : comments.length === 0 ? (
                <p className="empty-state">Комментариев пока нет.</p>
              ) : (
                comments.map((comment) => {
                  const author = members.find((member) => member.id === comment.author_id)
                  const canDeleteComment = canCreate || comment.author_id === user.id

                  return (
                    <article className="comment-item" key={comment.id}>
                      <div>
                        <strong>{author?.email ?? `Пользователь #${comment.author_id}`}</strong>
                        <span>{formatDate(comment.created_at)}</span>
                        <p>{comment.text}</p>
                      </div>
                      {canDeleteComment ? (
                        <button
                          className="icon-button danger"
                          type="button"
                          onClick={() => deleteComment(comment)}
                          title="Удалить комментарий"
                        >
                          <Trash2 size={16} />
                        </button>
                      ) : null}
                    </article>
                  )
                })
              )}
            </div>
          </div>
        ) : null}
      </section>
    </section>
  )
}

function TaskTable({
  compact = false,
  members = [],
  onAssigneeChange,
  onCommentsOpen,
  onDelete,
  onEvaluate,
  onStatusChange,
  selectedTaskId,
  tasks,
}: {
  compact?: boolean
  members?: User[]
  onAssigneeChange?: (task: Task, assigneeId: number | null) => void
  onCommentsOpen?: (task: Task) => void
  onDelete?: (task: Task) => void
  onEvaluate?: (task: Task, score: number) => void
  onStatusChange?: (task: Task, status: TaskStatus) => void
  selectedTaskId?: number | null
  tasks: Task[]
}) {
  if (tasks.length === 0) {
    return <p className="empty-state">Пока нет задач для отображения.</p>
  }

  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Название</th>
            <th>Статус</th>
            <th>Дедлайн</th>
            {!compact ? <th>Исполнитель</th> : null}
            {!compact ? <th>Действия</th> : null}
          </tr>
        </thead>
        <tbody>
          {tasks.map((task) => (
            <tr className={selectedTaskId === task.id ? 'selected-row' : ''} key={task.id}>
              <td>
                <strong>{task.title}</strong>
                {!compact && task.description ? <span>{task.description}</span> : null}
              </td>
              <td>
                {onStatusChange ? (
                  <select
                    value={task.status}
                    onChange={(event) =>
                      onStatusChange(task, event.target.value as TaskStatus)
                    }
                  >
                    <option value="open">Открыта</option>
                    <option value="in_progress">В работе</option>
                    <option value="done">Готово</option>
                  </select>
                ) : (
                  <span className={`status ${task.status}`}>{statusLabel(task.status)}</span>
                )}
              </td>
              <td>{formatDate(task.deadline)}</td>
              {!compact ? (
                <td>
                  {onAssigneeChange ? (
                    <select
                      value={task.assignee_id ?? ''}
                      onChange={(event) =>
                        onAssigneeChange(
                          task,
                          event.target.value ? Number(event.target.value) : null,
                        )
                      }
                    >
                      <option value="">Без исполнителя</option>
                      {members.map((member) => (
                        <option key={member.id} value={member.id}>
                          {memberLabel(member)}
                        </option>
                      ))}
                    </select>
                  ) : task.assignee_id ? (
                    members.find((member) => member.id === task.assignee_id)?.email ??
                    `#${task.assignee_id}`
                  ) : (
                    '—'
                  )}
                </td>
              ) : null}
              {!compact ? (
                <td>
                  <div className="row-actions">
                    {onCommentsOpen ? (
                      <button
                        className="secondary-button compact-button"
                        type="button"
                        onClick={() => onCommentsOpen(task)}
                      >
                        Комментарии
                      </button>
                    ) : null}
                    {onEvaluate && task.status === 'done' ? (
                      <select
                        defaultValue=""
                        title="Поставить оценку"
                        onChange={(event) => {
                          if (event.target.value) {
                            onEvaluate(task, Number(event.target.value))
                            event.currentTarget.value = ''
                          }
                        }}
                      >
                        <option value="">Оценка</option>
                        {[1, 2, 3, 4, 5].map((score) => (
                          <option key={score} value={score}>
                            {score}
                          </option>
                        ))}
                      </select>
                    ) : null}
                    {onDelete ? (
                      <button
                        className="icon-button danger"
                        type="button"
                        onClick={() => onDelete(task)}
                        title="Удалить задачу"
                      >
                        <Trash2 size={16} />
                      </button>
                    ) : null}
                  </div>
                </td>
              ) : null}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function TeamPage({
  notify,
  onUserChange,
  token,
  user,
}: {
  notify: (message: string) => void
  onUserChange: (user: User) => void
  token: string
  user: User
}) {
  const [team, setTeam] = useState<TeamWithMembers | null>(null)
  const [teamName, setTeamName] = useState('')
  const [joinCode, setJoinCode] = useState('')
  const [createdJoinCode, setCreatedJoinCode] = useState<string | null>(null)
  const [teamJoinCode, setTeamJoinCode] = useState<string | null>(null)
  const canManageTeam = user.role === 'admin'

  const loadTeam = useCallback(async () => {
    try {
      setTeam(await api.getMyTeam(token))
    } catch (error) {
      if (error instanceof ApiError && error.status === 409) {
        setTeam(null)
      } else {
        notify(getErrorMessage(error, 'Не удалось загрузить команду.'))
      }
    }
  }, [notify, token])

  const loadTeamJoinCode = useCallback(async () => {
    if (!canManageTeam) {
      setTeamJoinCode(null)
      return
    }

    try {
      const data = await api.getMyTeamJoinCode(token)
      setTeamJoinCode(data.join_code)
    } catch (error) {
      setTeamJoinCode(null)
      if (!(error instanceof ApiError && error.status === 409)) {
        notify(getErrorMessage(error, 'Не удалось загрузить код приглашения.'))
      }
    }
  }, [canManageTeam, notify, token])

  useEffect(() => {
    void loadTeam()
    void loadTeamJoinCode()
  }, [loadTeam, loadTeamJoinCode])

  async function createTeam(event: FormEvent) {
    event.preventDefault()
    try {
      const created = await api.createTeam(token, teamName)
      setCreatedJoinCode(created.join_code)
      setTeamJoinCode(created.join_code)
      setTeamName('')
      onUserChange(await api.me(token))
      notify('Команда создана.')
      await loadTeam()
    } catch (error) {
      notify(getErrorMessage(error, 'Не удалось создать команду.'))
    }
  }

  async function joinTeam(event: FormEvent) {
    event.preventDefault()
    try {
      const updatedUser = await api.joinTeam(token, joinCode)
      onUserChange(updatedUser)
      setJoinCode('')
      notify('Вы вступили в команду.')
      await loadTeam()
    } catch (error) {
      notify(getErrorMessage(error, 'Не удалось вступить в команду.'))
    }
  }

  async function updateRole(memberId: number, role: UserRole) {
    try {
      await api.updateMemberRole(token, memberId, role)
      await loadTeam()
    } catch (error) {
      notify(getErrorMessage(error, 'Не удалось изменить роль.'))
    }
  }

  async function removeMember(memberId: number) {
    try {
      await api.removeMember(token, memberId)
      await loadTeam()
    } catch (error) {
      notify(getErrorMessage(error, 'Не удалось удалить участника.'))
    }
  }

  const canCreate = canManageTeam

  return (
    <section className="view-grid two-column">
      <section className="panel">
        <div className="panel-heading">
          <div>
            <h2>Моя команда</h2>
            <p>{team ? `Участников: ${team.users.length}` : 'Вы пока не в команде'}</p>
          </div>
          <button className="icon-button" type="button" onClick={loadTeam} title="Обновить">
            <RefreshCcw size={18} />
          </button>
        </div>

        {team ? (
          <>
            <dl className="detail-list compact">
              <div>
                <dt>Название</dt>
                <dd>{team.name}</dd>
              </div>
              <div>
                <dt>ID</dt>
                <dd>{team.id}</dd>
              </div>
              {canManageTeam && teamJoinCode ? (
                <div>
                  <dt>Код приглашения</dt>
                  <dd>{teamJoinCode}</dd>
                </div>
              ) : null}
            </dl>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Пользователь</th>
                    <th>Роль</th>
                    <th>Команда</th>
                    <th>Действия</th>
                  </tr>
                </thead>
                <tbody>
                  {team.users.map((member) => (
                    <tr key={member.id}>
                      <td>
                        <strong>{member.email}</strong>
                        <span>#{member.id}</span>
                      </td>
                      <td>
                        <select
                          value={member.role}
                          disabled={!canManageTeam || member.id === user.id}
                          onChange={(event) =>
                            updateRole(member.id, event.target.value as UserRole)
                          }
                        >
                          <option value="user">Сотрудник</option>
                          <option value="manager">Менеджер</option>
                          <option value="admin">Администратор</option>
                        </select>
                      </td>
                      <td>{member.team_id ?? '—'}</td>
                      <td>
                        <button
                          className="icon-button danger"
                          type="button"
                          disabled={!canManageTeam || member.id === user.id}
                          onClick={() => removeMember(member.id)}
                          title="Удалить участника"
                        >
                          <Trash2 size={16} />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        ) : (
          <p className="empty-state">
            Вступите в команду по коду или создайте новую, если у вас есть роль администратора.
          </p>
        )}
      </section>

      <section className="panel stack">
        {team ? (
          <div className="form-stack">
            <h2>Вы уже в команде</h2>
            {canManageTeam ? (
              <p className="hint">
                Вы администратор команды «{team.name}». Смена команды сейчас не
                поддерживается через интерфейс.
              </p>
            ) : (
              <p className="hint">
                Сейчас вы состоите в команде «{team.name}». Чтобы перейти в другую
                команду, администратор должен сначала удалить вас из текущей.
              </p>
            )}
          </div>
        ) : (
          <>
            {canCreate ? (
              <form className="form-stack" onSubmit={createTeam}>
                <h2>Создать команду</h2>
                <label>
                  Название команды
                  <input
                    value={teamName}
                    onChange={(event) => setTeamName(event.target.value)}
                    required
                  />
                </label>
                <button className="primary-button" type="submit">
                  Создать
                </button>
                {createdJoinCode ? (
                  <p className="hint">
                    Код приглашения: <strong>{createdJoinCode}</strong>
                  </p>
                ) : null}
              </form>
            ) : null}

            <form className="form-stack" onSubmit={joinTeam}>
              <h2>Вступить в команду</h2>
              <label>
                Код приглашения
                <input
                  value={joinCode}
                  onChange={(event) => setJoinCode(event.target.value)}
                  required
                />
              </label>
              <button className="secondary-button" type="submit">
                Вступить
              </button>
            </form>
          </>
        )}
      </section>
    </section>
  )
}

function CalendarPage({
  notify,
  token,
}: {
  notify: (message: string) => void
  token: string
}) {
  const defaultStart = useMemo(() => {
    const date = new Date()
    date.setHours(0, 0, 0, 0)
    return toInputDateTime(date)
  }, [])
  const defaultEnd = useMemo(() => toInputDateTime(addDays(new Date(), 7)), [])
  const [startsAt, setStartsAt] = useState(defaultStart)
  const [endsAt, setEndsAt] = useState(defaultEnd)
  const [calendar, setCalendar] = useState<CalendarRead>({ tasks: [], meetings: [] })
  const [members, setMembers] = useState<User[]>([])
  const [meetingForm, setMeetingForm] = useState(emptyMeetingForm)

  const loadCalendar = useCallback(async () => {
    const start = toApiDateTime(startsAt)
    const end = toApiDateTime(endsAt)
    if (!start || !end) return
    try {
      setCalendar(await api.getCalendar(token, start, end))
    } catch (error) {
      notify(getErrorMessage(error, 'Не удалось загрузить календарь.'))
    }
  }, [endsAt, notify, startsAt, token])

  const loadTeamMembers = useCallback(async () => {
    try {
      const team = await api.getMyTeam(token)
      setMembers(team.users)
    } catch {
      setMembers([])
    }
  }, [token])

  useEffect(() => {
    void loadCalendar()
    void loadTeamMembers()
  }, [loadCalendar, loadTeamMembers])

  async function createMeeting(event: FormEvent) {
    event.preventDefault()
    const start = toApiDateTime(meetingForm.startsAt)
    const end = toApiDateTime(meetingForm.endsAt)
    if (!start || !end) return

    try {
      await api.createMeeting(token, {
        title: meetingForm.title,
        description: meetingForm.description || null,
        starts_at: start,
        ends_at: end,
        participant_id: Number(meetingForm.participantId),
      })
      setMeetingForm(emptyMeetingForm())
      notify('Встреча создана.')
      await loadCalendar()
    } catch (error) {
      notify(getErrorMessage(error, 'Не удалось создать встречу.'))
    }
  }

  async function cancelMeeting(meeting: Meeting) {
    try {
      await api.cancelMeeting(token, meeting.id)
      notify('Встреча отменена.')
      await loadCalendar()
    } catch (error) {
      notify(getErrorMessage(error, 'Не удалось отменить встречу.'))
    }
  }

  return (
    <section className="view-grid">
      <section className="panel">
        <div className="panel-heading">
          <div>
            <h2>Период</h2>
            <p>Выберите даты, за которые нужно показать задачи и встречи.</p>
          </div>
          <button className="icon-button" type="button" onClick={loadCalendar} title="Обновить">
            <RefreshCcw size={18} />
          </button>
        </div>
        <div className="range-row">
          <label>
            Начало
            <input
              type="datetime-local"
              value={startsAt}
              onChange={(event) => setStartsAt(event.target.value)}
            />
          </label>
          <label>
            Конец
            <input
              type="datetime-local"
              value={endsAt}
              onChange={(event) => setEndsAt(event.target.value)}
            />
          </label>
        </div>
      </section>

      <section className="panel">
        <div className="panel-heading">
          <div>
            <h2>Задачи в календаре</h2>
            <p>Задач с дедлайном: {calendar.tasks.length}</p>
          </div>
        </div>
        <TaskTable tasks={calendar.tasks} compact />
      </section>

      <section className="panel">
        <div className="panel-heading">
          <div>
            <h2>Встречи</h2>
            <p>Встреч в выбранном периоде: {calendar.meetings.length}</p>
          </div>
        </div>
        <div className="meeting-list">
          {calendar.meetings.length === 0 ? (
            <p className="empty-state">В этом периоде встреч нет.</p>
          ) : (
            calendar.meetings.map((meeting) => (
              <div className="meeting-row" key={meeting.id}>
                <div>
                  <strong>{meeting.title}</strong>
                  <span>
                    {formatDate(meeting.starts_at)} — {formatDate(meeting.ends_at)}
                  </span>
                </div>
                <button
                  className="icon-button danger"
                  type="button"
                  onClick={() => cancelMeeting(meeting)}
                  title="Отменить встречу"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            ))
          )}
        </div>
      </section>

      <form className="panel form-grid" onSubmit={createMeeting}>
        <div className="panel-heading full">
          <div>
            <h2>Создать встречу</h2>
            <p>Менеджеры и администраторы могут запланировать встречу один-на-один с участником команды.</p>
          </div>
        </div>
        <label>
          Название
          <input
            value={meetingForm.title}
            onChange={(event) =>
              setMeetingForm({ ...meetingForm, title: event.target.value })
            }
            required
          />
        </label>
        <label>
          Участник
          <select
            value={meetingForm.participantId}
            onChange={(event) =>
              setMeetingForm({ ...meetingForm, participantId: event.target.value })
            }
            required
          >
            <option value="">Выберите участника</option>
            {members.map((member) => (
              <option key={member.id} value={member.id}>
                {memberLabel(member)}
              </option>
            ))}
          </select>
        </label>
        <label>
          Начало
          <input
            type="datetime-local"
            value={meetingForm.startsAt}
            onChange={(event) =>
              setMeetingForm({ ...meetingForm, startsAt: event.target.value })
            }
            required
          />
        </label>
        <label>
          Конец
          <input
            type="datetime-local"
            value={meetingForm.endsAt}
            onChange={(event) =>
              setMeetingForm({ ...meetingForm, endsAt: event.target.value })
            }
            required
          />
        </label>
        <label className="full">
          Описание
          <textarea
            value={meetingForm.description}
            onChange={(event) =>
              setMeetingForm({ ...meetingForm, description: event.target.value })
            }
            rows={3}
          />
        </label>
        <button className="primary-button" type="submit">
          Создать встречу
        </button>
      </form>
    </section>
  )
}

function ProfilePage({
  logout,
  notify,
  onUserChange,
  token,
  user,
}: {
  logout: () => void
  notify: (message: string) => void
  onUserChange: (user: User) => void
  token: string
  user: User
}) {
  const [email, setEmail] = useState(user.email)
  const [password, setPassword] = useState('')

  async function updateProfile(event: FormEvent) {
    event.preventDefault()
    const payload: { email?: string; password?: string } = {}
    if (email && email !== user.email) payload.email = email
    if (password) payload.password = password

    try {
      const updated = await api.updateMe(token, payload)
      onUserChange(updated)
      setPassword('')
      notify('Профиль обновлён.')
    } catch (error) {
      notify(getErrorMessage(error, 'Не удалось обновить профиль.'))
    }
  }

  async function deactivate() {
    try {
      await api.deactivateMe(token)
      notify('Аккаунт отключён.')
      logout()
    } catch (error) {
      notify(getErrorMessage(error, 'Не удалось отключить аккаунт.'))
    }
  }

  return (
    <section className="view-grid two-column">
      <form className="panel form-stack" onSubmit={updateProfile}>
        <div className="panel-heading">
          <div>
            <h2>Профиль</h2>
            <p>Здесь можно изменить email или пароль.</p>
          </div>
          <Save size={20} />
        </div>
        <label>
          Email
          <input
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            required
          />
        </label>
        <label>
          Новый пароль
          <input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            minLength={8}
            placeholder="Оставьте пустым, если пароль менять не нужно"
          />
        </label>
        <button className="primary-button" type="submit">
          Сохранить изменения
        </button>
      </form>

      <section className="panel stack">
        <div className="panel-heading">
          <div>
            <h2>Статус аккаунта</h2>
            <p>Отключённый аккаунт больше не сможет пользоваться API.</p>
          </div>
          <Star size={20} />
        </div>
        <dl className="detail-list">
          <div>
            <dt>Статус</dt>
            <dd>{user.is_active ? 'Активен' : 'Отключён'}</dd>
          </div>
          <div>
            <dt>Роль</dt>
            <dd>{roleLabel(user.role)}</dd>
          </div>
        </dl>
        <button className="danger-button" type="button" onClick={deactivate}>
          Отключить аккаунт
        </button>
      </section>
    </section>
  )
}

export default App
