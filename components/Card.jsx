import React from 'react';
export default function Card({ title, value, sub, tone = "neutral" }) {
  return (
    <div className={`sx-card sx-card--${tone}`}>
      <div className="sx-card__title">{title}</div>
      <div className="sx-card__value">{value}</div>
      {sub && <div className="sx-card__sub">{sub}</div>}
    </div>
  );
}
