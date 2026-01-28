'use client';

interface FilterPanelProps {
  durationPreference: string;
  uploadDate: string;
  onDurationChange: (value: string) => void;
  onUploadDateChange: (value: string) => void;
}

export default function FilterPanel({
  durationPreference,
  uploadDate,
  onDurationChange,
  onUploadDateChange,
}: FilterPanelProps) {
  return (
    <div className="filter-panel">
      <div className="filter-group">
        <label className="filter-label">Video Duration</label>
        <select
          value={durationPreference}
          onChange={(e) => onDurationChange(e.target.value)}
          className="filter-select"
        >
          <option value="any">Any length</option>
          <option value="short">Short (&lt; 10 min)</option>
          <option value="medium">Medium (10-30 min)</option>
          <option value="long">Long (&gt; 30 min)</option>
        </select>
      </div>

      <div className="filter-group">
        <label className="filter-label">Upload Date</label>
        <select
          value={uploadDate}
          onChange={(e) => onUploadDateChange(e.target.value)}
          className="filter-select"
        >
          <option value="any">Any time</option>
          <option value="week">Past week</option>
          <option value="month">Past month</option>
          <option value="year">Past year</option>
        </select>
      </div>
    </div>
  );
}
