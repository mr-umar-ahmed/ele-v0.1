function HUDButton({ icon, top }) {

  return (

    <div
      className="hud-floating-btn"
      style={{ top }}
    >

      {icon}

    </div>

  );
}

export default HUDButton;