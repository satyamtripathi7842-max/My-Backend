import React from "react";
export default function SeverityBadge({ severity }) {
  return <span className={`sx-badge sx-badge--${severity}`}>{severity?.toUpperCase()}</span>;
}
