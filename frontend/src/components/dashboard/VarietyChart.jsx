import ReactECharts from 'echarts-for-react';

const COLORS = [
  '#2563eb',
  '#0d9488',
  '#7c3aed',
  '#ea580c',
  '#db2777',
  '#65a30d',
];

function numeric(value) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}

function quantile(sorted, fraction) {
  if (!sorted.length) return 0;
  const position = (sorted.length - 1) * fraction;
  const lower = Math.floor(position);
  const upper = Math.ceil(position);
  if (lower === upper) return sorted[lower];
  return sorted[lower] + (sorted[upper] - sorted[lower]) * (position - lower);
}

function getHistogram(values, binCount = 12) {
  if (!values.length) return { labels: [], counts: [] };
  const min = Math.min(...values);
  const max = Math.max(...values);
  if (min === max) return { labels: [String(min)], counts: [values.length] };
  const width = (max - min) / binCount;
  const counts = Array(binCount).fill(0);
  values.forEach((value) => {
    const index = Math.min(binCount - 1, Math.floor((value - min) / width));
    counts[index] += 1;
  });
  const labels = counts.map((_, index) => {
    const start = min + index * width;
    const end = start + width;
    return `${start.toLocaleString(undefined, { maximumFractionDigits: 1 })}–${end.toLocaleString(undefined, { maximumFractionDigits: 1 })}`;
  });
  return { labels, counts };
}

function buildOption(chart, data) {
  const type = chart.chart_type;
  const axisBase = {
    axisLabel: { color: '#64748b', fontSize: 11, hideOverlap: true },
    axisLine: { lineStyle: { color: '#e2e8f0' } },
    axisTick: { show: false },
  };
  const gridBase = {
    top: 28,
    right: 24,
    bottom: 55,
    left: 55,
    containLabel: true,
  };

  if (type === 'histogram') {
    const values = data
      .map((row) => numeric(row.value))
      .filter((value) => value !== null);
    const { labels, counts } = getHistogram(values);
    return {
      tooltip: { trigger: 'axis' },
      grid: gridBase,
      xAxis: {
        type: 'category',
        data: labels,
        ...axisBase,
        axisLabel: { ...axisBase.axisLabel, rotate: 30 },
      },
      yAxis: {
        type: 'value',
        name: 'Frequency',
        ...axisBase,
        splitLine: { lineStyle: { type: 'dashed', color: '#e2e8f0' } },
      },
      series: [
        {
          name: 'Frequency',
          type: 'bar',
          data: counts,
          barGap: '0%',
          itemStyle: { color: COLORS[0], borderRadius: [4, 4, 0, 0] },
        },
      ],
    };
  }

  if (type === 'boxplot') {
    const values = data
      .map((row) => numeric(row.value))
      .filter((value) => value !== null)
      .sort((a, b) => a - b);
    if (!values.length) return {};
    const summary = [
      values[0],
      quantile(values, 0.25),
      quantile(values, 0.5),
      quantile(values, 0.75),
      values[values.length - 1],
    ];
    return {
      tooltip: { trigger: 'item' },
      grid: { ...gridBase, bottom: 35 },
      xAxis: {
        type: 'category',
        data: [chart.column || 'Distribution'],
        ...axisBase,
      },
      yAxis: {
        type: 'value',
        ...axisBase,
        splitLine: { lineStyle: { type: 'dashed', color: '#e2e8f0' } },
      },
      series: [
        {
          name: chart.column || 'Distribution',
          type: 'boxplot',
          data: [summary],
          itemStyle: { color: '#dbeafe', borderColor: COLORS[0] },
          emphasis: { itemStyle: { borderColor: '#1d4ed8' } },
        },
      ],
    };
  }

  if (type === 'heatmap') {
    const xName = chart.x_column;
    const yName = chart.y_column;
    const points = data
      .map((row) => [numeric(row[xName]), numeric(row[yName])])
      .filter(([x, y]) => x !== null && y !== null);
    if (!points.length) return {};
    const xMin = Math.min(...points.map((p) => p[0]));
    const xMax = Math.max(...points.map((p) => p[0]));
    const yMin = Math.min(...points.map((p) => p[1]));
    const yMax = Math.max(...points.map((p) => p[1]));
    const bins = 10;
    const cellCounts = new Map();
    points.forEach(([x, y]) => {
      const xi =
        xMax === xMin
          ? 0
          : Math.min(bins - 1, Math.floor(((x - xMin) / (xMax - xMin)) * bins));
      const yi =
        yMax === yMin
          ? 0
          : Math.min(bins - 1, Math.floor(((y - yMin) / (yMax - yMin)) * bins));
      const key = `${xi},${yi}`;
      cellCounts.set(key, (cellCounts.get(key) || 0) + 1);
    });
    const heatData = Array.from(cellCounts.entries()).map(([key, count]) => {
      const [x, y] = key.split(',').map(Number);
      return [x, y, count];
    });
    const labels = Array.from({ length: bins }, (_, index) =>
      String(index + 1),
    );
    return {
      tooltip: {
        position: 'top',
        formatter: (params) =>
          `X bin: ${params.value[0] + 1}<br/>Y bin: ${params.value[1] + 1}<br/>Rows: ${params.value[2]}`,
      },
      grid: { top: 28, right: 25, bottom: 42, left: 48 },
      xAxis: {
        type: 'category',
        data: labels,
        name: xName,
        ...axisBase,
        splitArea: { show: true },
      },
      yAxis: {
        type: 'category',
        data: labels,
        name: yName,
        ...axisBase,
        splitArea: { show: true },
      },
      visualMap: {
        min: 0,
        max: Math.max(...heatData.map((item) => item[2]), 1),
        calculable: true,
        orient: 'horizontal',
        left: 'center',
        bottom: 0,
        textStyle: { color: '#64748b' },
      },
      series: [
        {
          name: 'Row density',
          type: 'heatmap',
          data: heatData,
          label: { show: false },
          emphasis: {
            itemStyle: { shadowBlur: 8, shadowColor: 'rgba(0,0,0,0.25)' },
          },
        },
      ],
    };
  }

  const categories = data.map((row) =>
    String(row?.[chart.group_by] ?? 'Unknown'),
  );
  const values = data.map((row) => numeric(row.value) ?? 0);

  if (type === 'donut') {
    return {
      tooltip: { trigger: 'item', formatter: '{b}<br/>{c} ({d}%)' },
      legend: {
        type: 'scroll',
        bottom: 0,
        textStyle: { color: '#64748b', fontSize: 11 },
      },
      series: [
        {
          type: 'pie',
          radius: ['52%', '76%'],
          center: ['50%', '44%'],
          data: data.map((row) => ({
            name: String(row?.[chart.group_by] ?? 'Unknown'),
            value: numeric(row.value) ?? 0,
          })),
          itemStyle: { borderRadius: 5, borderColor: '#fff', borderWidth: 2 },
          label: { show: false },
          emphasis: { label: { show: true, formatter: '{b}\n{d}%' } },
        },
      ],
    };
  }

  if (type === 'radar') {
    const maxValue = Math.max(...values, 1);
    return {
      tooltip: { trigger: 'item' },
      radar: {
        indicator: categories.map((name) => ({ name, max: maxValue * 1.15 })),
        radius: '65%',
        axisName: { color: '#64748b', fontSize: 11 },
        splitLine: { lineStyle: { color: '#e2e8f0' } },
        splitArea: {
          areaStyle: {
            color: ['rgba(37,99,235,0.02)', 'rgba(37,99,235,0.05)'],
          },
        },
      },
      series: [
        {
          type: 'radar',
          data: [
            {
              value: values,
              name: chart.column || chart.operation || 'Average',
            },
          ],
          areaStyle: { color: 'rgba(37,99,235,0.16)' },
          lineStyle: { color: COLORS[0], width: 2 },
          itemStyle: { color: COLORS[0] },
        },
      ],
    };
  }

  if (type === 'horizontal_bar') {
    return {
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      grid: gridBase,
      xAxis: {
        type: 'value',
        ...axisBase,
        splitLine: { lineStyle: { type: 'dashed', color: '#e2e8f0' } },
      },
      yAxis: {
        type: 'category',
        data: categories,
        ...axisBase,
        axisLabel: { ...axisBase.axisLabel, width: 100, overflow: 'truncate' },
      },
      series: [
        {
          type: 'bar',
          data: values,
          barMaxWidth: 28,
          itemStyle: { color: COLORS[1], borderRadius: [0, 5, 5, 0] },
        },
      ],
    };
  }

  const isArea = type === 'area';
  return {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: gridBase,
    xAxis: {
      type: 'category',
      data: categories,
      ...axisBase,
      axisLabel: {
        ...axisBase.axisLabel,
        rotate: categories.length > 8 ? 30 : 0,
      },
    },
    yAxis: {
      type: 'value',
      ...axisBase,
      splitLine: { lineStyle: { type: 'dashed', color: '#e2e8f0' } },
    },
    series: [
      {
        type: isArea ? 'line' : 'bar',
        data: values,
        smooth: isArea,
        showSymbol: isArea && values.length <= 30,
        symbolSize: 6,
        areaStyle: isArea ? { color: 'rgba(13,148,136,0.18)' } : undefined,
        lineStyle: isArea ? { color: COLORS[1], width: 2.5 } : undefined,
        itemStyle: {
          color: isArea ? COLORS[1] : COLORS[0],
          borderRadius: isArea ? 0 : [5, 5, 0, 0],
        },
      },
    ],
  };
}

function VarietyChart({ chart, data = [] }) {
  const safeData = Array.isArray(data) ? data : [];
  const option = buildOption(chart || {}, safeData);
  if (!safeData.length) {
    return (
      <div className='flex h-[300px] items-center justify-center rounded-xl border border-dashed border-stone-200 bg-stone-50/50 text-sm text-slate-500'>
        No chart data available.
      </div>
    );
  }
  return (
    <div className='w-full overflow-hidden rounded-xl'>
      <ReactECharts
        option={option}
        style={{ width: '100%', height: '300px' }}
        opts={{ renderer: 'canvas' }}
        notMerge
        lazyUpdate
      />
    </div>
  );
}

export default VarietyChart;
