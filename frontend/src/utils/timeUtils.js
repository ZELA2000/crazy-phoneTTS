/**
 * Utilità per formattazione tempo
 */

export const formatTime = (seconds) => {
  if (seconds < 60) {
    return `${seconds.toFixed(1)}s`;
  } else {
    const minutes = Math.floor(seconds / 60);
    const secs = (seconds % 60).toFixed(1);
    return `${minutes}m ${secs}s`;
  }
};

export const parseTimeInput = (value, unit) => {
  const numValue = parseFloat(value) || 0;
  switch(unit) {
    case 'minutes': return numValue * 60;
    case 'seconds': return numValue;
    default: return numValue;
  }
};
