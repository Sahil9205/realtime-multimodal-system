export type ConnectionState = 'idle' | 'connecting' | 'ready' | 'recording' | 'thinking' | 'speaking' | 'error'

export type TimelineItem = {
  id: number
  role: 'user' | 'assistant' | 'system'
  text: string
  final?: boolean
}

type TranscriptEvent = {
  type: 'transcript'
  text: string
  final: boolean
}

type ResponseEvent = {
  type: 'response'
  text: string
}

type ReadyEvent = {
  type: 'ready'
}

export type AudioEvent = {
  type: 'audio'
  sample_rate: number
  channels: number
  encoding: string
}

export type ServerEvent = TranscriptEvent | ResponseEvent | ReadyEvent | AudioEvent
