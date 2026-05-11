function ReactorCore({ status }) {

  return (

    <div className={`reactor ${status.toLowerCase()}`}>

      <div className="ring outer-ring"></div>

      <div className="ring middle-ring"></div>

      <div className="ring inner-ring"></div>

      <div className="reactor-lines"></div>

      <div className="core-center">

        <span className="core-text">
          ELE
        </span>

      </div>

    </div>

  );
}

export default ReactorCore;