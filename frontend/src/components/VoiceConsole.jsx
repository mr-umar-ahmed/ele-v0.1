function VoiceConsole({
  transcript,
  response,
  status
}) {

  return (

    <div className="voice-console">

      <div className="console-header">

        COMMAND_INTERFACE

      </div>

      <div className="console-body">

        {
          transcript && (

            <div className="console-line user-line">

              <span className="console-tag">
                USER
              </span>

              <span className="console-content">
                {transcript}
              </span>

            </div>

          )
        }

        {
          response && (

            <div className="console-line ai-line">

              <span className="console-tag">
                ELE
              </span>

              <span className="console-content">
                {response}
              </span>

            </div>

          )
        }

        {
          !transcript &&
          !response && (

            <div className="console-idle">

              Awaiting command...

            </div>

          )
        }

      </div>

      <div className="console-footer">

        STATUS:
        <span className={`status-text ${status.toLowerCase()}`}>
          {status}
        </span>

      </div>

    </div>

  );
}

export default VoiceConsole;