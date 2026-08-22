"use client";

import {
  useEffect,
  useRef,
  useState,
} from "react";

interface VoiceAssistantProps {
  onTranscript: (text: string) => void;
  language: string;
}

interface SpeechRecognitionEvent
  extends Event {
  results: SpeechRecognitionResultList;
}

interface SpeechRecognitionErrorEvent
  extends Event {
  error: string;
}

interface SpeechRecognitionInstance {
  continuous: boolean;
  interimResults: boolean;
  lang: string;

  start: () => void;
  stop: () => void;

  onresult:
    | ((event: SpeechRecognitionEvent) => void)
    | null;

  onerror:
    | ((event: SpeechRecognitionErrorEvent) => void)
    | null;

  onend:
    | (() => void)
    | null;
}

interface SpeechRecognitionConstructor {
  new (): SpeechRecognitionInstance;
}

declare global {
  interface Window {
    SpeechRecognition?: SpeechRecognitionConstructor;
    webkitSpeechRecognition?: SpeechRecognitionConstructor;
  }
}

export default function VoiceAssistant({
  onTranscript,
  language,
}: VoiceAssistantProps) {
  const recognitionRef =
    useRef<SpeechRecognitionInstance | null>(
      null
    );

  const [listening, setListening] =
    useState(false);

  const [supported, setSupported] =
    useState(true);

  const [error, setError] =
    useState("");

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }

    const SpeechRecognition =
      window.SpeechRecognition ||
      window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      setSupported(false);
      return;
    }

    const recognition =
      new SpeechRecognition();

    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onresult = (
      event: SpeechRecognitionEvent
    ) => {
      const transcript =
        event.results[0][0].transcript;

      onTranscript(transcript);
    };

    recognition.onerror = (
      event: SpeechRecognitionErrorEvent
    ) => {
      setListening(false);
      setError(
        `Microphone error: ${event.error}`
      );
    };

    recognition.onend = () => {
      setListening(false);
    };

    recognitionRef.current = recognition;

    return () => {
      recognition.stop();
    };
  }, [onTranscript]);

  const getRecognitionLanguage =
    () => {
      switch (language) {
        case "Hindi":
          return "hi-IN";

        case "Portuguese":
          return "pt-BR";

        case "Russian":
          return "ru-RU";

        case "Chinese":
          return "zh-CN";

        case "English":
        default:
          return "en-IN";
      }
    };

  const startListening = () => {
    if (!recognitionRef.current) {
      return;
    }

    setError("");

    recognitionRef.current.lang =
      getRecognitionLanguage();

    recognitionRef.current.start();

    setListening(true);
  };

  const stopListening = () => {
    recognitionRef.current?.stop();
    setListening(false);
  };

  if (!supported) {
    return (
      <div className="voice-error">
        Your browser does not support
        Speech Recognition.
        <br />
        Please use Google Chrome or
        Microsoft Edge.
      </div>
    );
  }

  return (
    <div className="voice-container">
      <button
        className={
          listening
            ? "voice-button listening"
            : "voice-button"
        }
        onClick={
          listening
            ? stopListening
            : startListening
        }
      >
        <span className="mic-icon">
          {listening ? "⏹" : "🎙️"}
        </span>

        <span>
          {listening
            ? "Listening..."
            : "Start Talking"}
        </span>
      </button>

      {listening && (
        <div className="listening-indicator">
          <span />
          <span />
          <span />
          <span />
          <span />
        </div>
      )}

      {error && (
        <div className="voice-error">
          {error}
        </div>
      )}
    </div>
  );
}
