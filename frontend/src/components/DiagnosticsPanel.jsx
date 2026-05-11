function DiagnosticsPanel() {

  const bars = [82, 65, 92, 48, 76, 58];

  return (

    <div className="diag-bars">

      {
        bars.map((value, index) => (

          <div
            key={index}
            className="diag-row"
          >

            <span>D{index + 1}</span>

            <div className="diag-track">

              <div
                className="diag-fill"
                style={{
                  width: `${value}%`
                }}
              ></div>

            </div>

          </div>
        ))
      }

    </div>
  );
}

export default DiagnosticsPanel;