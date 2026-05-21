import React from "react";

export default function Buttons({ text, type = "button", onClick }) {
  return (
    <button type={type} className="primary-btn" onClick={onClick}>
      {text}
    </button>
  );
}
