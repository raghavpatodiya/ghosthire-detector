import { useEffect, useState } from "react";
import "./Odometer.css";

export default function Odometer({ value }) {
  const [digits, setDigits] = useState([]);

  useEffect(() => {
    const padded = value.toString().padStart(6, "0");
    setDigits(padded.split(""));
  }, [value]);

  return (
    <div className="odo-container">
      {digits.map((d, i) => (
        <div className="odo-slot" key={i}>
          <div
            className="odo-strip"
            style={{ transform: `translateY(-${d * 40}px)` }}
          >
            {[...Array(10).keys()].map(n => (
              <div className="odo-digit" key={n}>{n}</div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}