import { useCallback, useRef, useState } from 'react'
import type { AudioEvent, ConnectionState, ServerEvent, TimelineItem } from './types'

const TARGET_SAMPLE_RATE = 16_000

type VoiceSession = {
  state: ConnectionState
  error: string | null
  timeline: TimelineItem[]
  connect: () => Promise<void>
  disconnect: () => void
  toggleRecording: () => Promise<void>
}

function downsample(input: Float32Array, inputRate: number): Int16Array {
  if (inputRate === TARGET_SAMPLE_RATE) {
    return floatToPcm(input)
  }

  const ratio = inputRate / TARGET_SAMPLE_RATE
  const output = new Int16Array(Math.round(input.length / ratio))

  for (let index = 0; index < output.length; index += 1) {
    const sourceIndex = Math.min(input.length - 1, Math.round(index * ratio))
    output[index] = Math.max(-1, Math.min(1, input[sourceIndex])) * 0x7fff
  }

  return output
}

function floatToPcm(input: Float32Array): Int16Array {
  const output = new Int16Array(input.length)
  for (let index = 0; index < input.length; index += 1) {
    output[index] = Math.max(-1, Math.min(1, input[index])) * 0x7fff
  }
  return output
}

export function useVoiceSession(): VoiceSession {
  const [state, setState] = useState<ConnectionState>('idle')
  const [error, setError] = useState<string | null>(null)
  const [timeline, setTimeline] = useState<TimelineItem[]>([])
  const socketRef = useRef<WebSocket | null>(null)
  const audioContextRef = useRef<AudioContext | null>(null)
  const mediaStreamRef = useRef<MediaStream | null>(null)
  const sourceRef = useRef<MediaStreamAudioSourceNode | null>(null)
  const processorRef = useRef<ScriptProcessorNode | null>(null)
  const silentGainRef = useRef<GainNode | null>(null)
  const nextIdRef = useRef(1)
  const pendingAudioRef = useRef<AudioEvent | null>(null)
  const activeAudioRef = useRef<{ audio: HTMLAudioElement; url: string } | null>(null)

  const addTimeline = useCallback((item: Omit<TimelineItem, 'id'>) => {
    setTimeline((current) => [...current, { ...item, id: nextIdRef.current++ }])
  }, [])

  const stopPlayback = useCallback(() => {
    const active = activeAudioRef.current
    if (!active) return

    active.audio.pause()
    active.audio.src = ''
    URL.revokeObjectURL(active.url)
    activeAudioRef.current = null
  }, [])

  const playAudio = useCallback(async (data: ArrayBuffer) => {
    const event = pendingAudioRef.current
    pendingAudioRef.current = null
    if (!event) return

    stopPlayback()
    const blob = new Blob([data], { type: event.encoding })
    const url = URL.createObjectURL(blob)
    const audio = new Audio(url)
    activeAudioRef.current = { audio, url }
    setState('speaking')
    audio.onended = () => {
      URL.revokeObjectURL(url)
      if (activeAudioRef.current?.audio === audio) {
        activeAudioRef.current = null
        setState('ready')
      }
    }
    await audio.play().catch(() => undefined)
  }, [stopPlayback])

  const connect = useCallback(async () => {
    if (socketRef.current?.readyState === WebSocket.OPEN) return

    setState('connecting')
    setError(null)
    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
    const socket = new WebSocket(`${protocol}://${window.location.host}/ws`)
    socket.binaryType = 'arraybuffer'

    socket.onopen = () => {
      socket.send(JSON.stringify({ type: 'start' }))
    }
    socket.onmessage = async (message) => {
      if (typeof message.data !== 'string') {
        await playAudio(message.data)
        return
      }

      const event = JSON.parse(message.data) as ServerEvent
      if (event.type === 'ready') {
        setState('ready')
        addTimeline({ role: 'system', text: 'Voice channel ready.' })
      } else if (event.type === 'transcript') {
        setTimeline((current) => {
          const previous = current.at(-1)
          if (previous?.role === 'user' && !previous.final) {
            return [...current.slice(0, -1), { ...previous, text: event.text, final: event.final }]
          }
          return [...current, { id: nextIdRef.current++, role: 'user', text: event.text, final: event.final }]
        })
      } else if (event.type === 'response') {
        addTimeline({ role: 'assistant', text: event.text, final: true })
      } else if (event.type === 'audio') {
        pendingAudioRef.current = event
      }
    }
    socket.onerror = () => {
      setError('Could not connect to the voice server.')
      setState('error')
    }
    socket.onclose = () => {
      socketRef.current = null
      setState('idle')
    }
    socketRef.current = socket
  }, [addTimeline, playAudio])

  const toggleRecording = useCallback(async () => {
    if (state === 'recording') {
      socketRef.current?.send(JSON.stringify({ type: 'stop' }))
      processorRef.current?.disconnect()
      sourceRef.current?.disconnect()
      silentGainRef.current?.disconnect()
      mediaStreamRef.current?.getTracks().forEach((track) => track.stop())
      await audioContextRef.current?.close()
      processorRef.current = null
      sourceRef.current = null
      silentGainRef.current = null
      mediaStreamRef.current = null
      audioContextRef.current = null
      setState('thinking')
      return
    }

    await connect()
    const socket = socketRef.current
    if (!socket) return
    stopPlayback()
    if (socket.readyState === WebSocket.OPEN) socket.send(JSON.stringify({ type: 'interrupt' }))
    const stream = await navigator.mediaDevices.getUserMedia({
      audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: true },
    })
    const context = new AudioContext()
    const source = context.createMediaStreamSource(stream)
    const processor = context.createScriptProcessor(4096, 1, 1)
    const silentGain = context.createGain()
    silentGain.gain.value = 0
    processor.onaudioprocess = (event) => {
      if (socket.readyState !== WebSocket.OPEN) return
      const pcm = downsample(event.inputBuffer.getChannelData(0), context.sampleRate)
      socket.send(pcm.buffer.slice(0) as ArrayBuffer)
    }
    source.connect(processor)
    // Keep the processing graph active without playing microphone audio back
    // through the speakers, which was creating an ASR feedback loop.
    processor.connect(silentGain)
    silentGain.connect(context.destination)
    mediaStreamRef.current = stream
    audioContextRef.current = context
    sourceRef.current = source
    processorRef.current = processor
    silentGainRef.current = silentGain
    setState('recording')
  }, [connect, state, stopPlayback])

  const disconnect = useCallback(() => {
    stopPlayback()
    processorRef.current?.disconnect()
    sourceRef.current?.disconnect()
    silentGainRef.current?.disconnect()
    mediaStreamRef.current?.getTracks().forEach((track) => track.stop())
    void audioContextRef.current?.close()
    socketRef.current?.close()
    processorRef.current = null
    sourceRef.current = null
    silentGainRef.current = null
    mediaStreamRef.current = null
    audioContextRef.current = null
    setState('idle')
  }, [stopPlayback])

  return { state, error, timeline, connect, disconnect, toggleRecording }
}
