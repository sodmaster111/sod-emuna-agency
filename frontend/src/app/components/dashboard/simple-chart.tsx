interface SimpleChartProps {
  data: { label: string; value: number }[];
  title: string;
}

export default function SimpleChart({ data, title }: SimpleChartProps) {
  const maxValue = Math.max(...data.map((item) => item.value), 0);
  const hasData = data.length > 0 && maxValue > 0;
  const barWidth = 28;
  const gap = 18;
  const chartHeight = 160;
  const labelHeight = 28;
  const chartWidth = data.length * (barWidth + gap) + gap;
  const gradientId = `barGradient-${title.replace(/\s+/g, "-").toLowerCase()}`;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h4 className="text-base font-semibold text-white">{title}</h4>
        {hasData && <p className="text-xs text-slate-400">Max: {maxValue}</p>}
      </div>
      {hasData ? (
        <svg
          viewBox={`0 0 ${chartWidth} ${chartHeight + labelHeight}`}
          className="h-56 w-full"
          role="img"
          aria-label={title}
        >
          <defs>
            <linearGradient id={gradientId} x1="0" x2="0" y1="0" y2="1">
              <stop offset="0%" stopColor="var(--color-accent, #22d3ee)" stopOpacity="0.9" />
              <stop offset="100%" stopColor="var(--color-accent, #22d3ee)" stopOpacity="0.4" />
            </linearGradient>
          </defs>
          {data.map((item, index) => {
            const barHeight = maxValue ? (item.value / maxValue) * chartHeight : 0;
            const x = gap + index * (barWidth + gap);
            const y = chartHeight - barHeight;

            return (
              <g key={item.label}>
                <rect
                  x={x}
                  y={y}
                  width={barWidth}
                  height={barHeight}
                  rx={6}
                  fill={`url(#${gradientId})`}
                  className="transition-opacity hover:opacity-90"
                />
                <text
                  x={x + barWidth / 2}
                  y={chartHeight + 14}
                  textAnchor="middle"
                  className="fill-slate-300 text-[10px]"
                >
                  {item.label}
                </text>
                <text
                  x={x + barWidth / 2}
                  y={y - 8}
                  textAnchor="middle"
                  className="fill-slate-200 text-[11px]"
                >
                  {item.value}
                </text>
              </g>
            );
          })}
        </svg>
      ) : (
        <p className="rounded-lg border border-white/10 bg-slate-900/60 p-4 text-sm text-slate-300">
          No data available for this chart.
        </p>
      )}
    </div>
  );
}
