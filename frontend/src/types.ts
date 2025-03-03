interface MenuButton {
  label: string;
  callback: (...args: any[]) => void;
  active: boolean;
  alwaysEnabled?: boolean;
}

type LogLevel = "TRACE" | "DEBUG" | "INFO" | "WARNING" | "ERROR" | "FATAL";

interface LogMessage {
  level: LogLevel;
  message: string;
  timestamp: string;
  source_file?: string;
  function_name?: string;
  line_number?: number;
}
