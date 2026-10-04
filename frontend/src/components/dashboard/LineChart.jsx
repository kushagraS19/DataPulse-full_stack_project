import ReactECharts from 'echarts-for-react';

function isDateLike(value) {
  if (value instanceof Date) return !Number.isNaN(value.getTime());

  if (typeof value !== 'string') return false;

  const trimmed = value.trim();

  if (!trimmed) return false;

  // Only treat strings with a clear date/time shape as dates.
  // This avoids converting ordinary categorical labels such as "2025".
  const datePattern =
    /^\d{4}[-/]\d{1,2}[-/]\d{1,2}(?:[T\s].*)?$|^\d{1,2}[-/]\d{1,2}[-/]\d{4}(?:[T\s].*)?$/;

  return datePattern.test(trimmed) && !Number.isNaN(Date.parse(trimmed));
}

function parseDate(value) {
  const date = value instanceof Date ? value : new Date(value);
  return Number.isNaN(date.getTime()) ? null : date;
}

function formatDateLabel(value, spanDays) {
  const date = parseDate(value);

  if (!date) return String(value ?? '');

  if (spanDays > 365) {
    return date.toLocaleDateString('en-IN', {
      month: 'short',
      year: 'numeric',
    });
  }

  if (spanDays > 31) {
    return date.toLocaleDateString('en-IN', {
      day: '2-digit',
      month: 'short',
    });
  }

  return date.toLocaleDateString('en-IN', {
    day: '2-digit',
    month: 'short',
  });
}

function formatTooltipDate(value, isDateAxis) {
  if (!isDateAxis) return String(value ?? '');

  const date = parseDate(value);

  if (!date) return String(value ?? '');

  return date.toLocaleString('en-IN', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: date.getHours() || date.getMinutes() ? '2-digit' : undefined,
    minute: date.getHours() || date.getMinutes() ? '2-digit' : undefined,
  });
}

function LineChart({ chart, data = [] }) {
  const rawRows = Array.isArray(data) ? data : [];

  const rows = rawRows
    .map((item, index) => ({
      ...item,
      __index: index,
      __xValue: item?.[chart?.group_by],
      __value: item?.value,
    }))
    .filter((item) => item.__xValue !== undefined && item.__xValue !== null);

  const isDateAxis =
    rows.length >= 2 && rows.every((item) => isDateLike(item.__xValue));

  const sortedRows = isDateAxis
    ? [...rows].sort((a, b) => {
        const first = parseDate(a.__xValue)?.getTime() ?? a.__index;
        const second = parseDate(b.__xValue)?.getTime() ?? b.__index;
        return first - second;
      })
    : rows;

  const dateValues = isDateAxis
    ? sortedRows
        .map((item) => parseDate(item.__xValue)?.getTime())
        .filter(Number.isFinite)
    : [];

  const spanDays =
    dateValues.length >= 2
      ? (Math.max(...dateValues) - Math.min(...dateValues)) /
        (1000 * 60 * 60 * 24)
      : 0;

  const categories = sortedRows.map((item) => item.__xValue);
  const values = sortedRows.map((item) => item.__value);

  const displayCategories = isDateAxis
    ? categories.map((value) => formatDateLabel(value, spanDays))
    : categories.map((value) => String(value));

  const option = {
    animation: true,
    animationDuration: 650,
    animationEasing: 'cubicOut',

    tooltip: {
      trigger: 'axis',
      confine: true,

      backgroundColor: 'rgba(255, 255, 255, 0.96)',
      borderColor: '#e7e5e4',
      borderWidth: 1,
      padding: [10, 12],
      extraCssText:
        'box-shadow: 0 12px 30px rgba(15, 23, 42, 0.10); border-radius: 10px;',

      textStyle: {
        color: '#334155',
        fontSize: 12,
      },

      formatter: (params) => {
        const point = params?.[0];

        if (!point) return '';

        const originalValue = categories[point.dataIndex];
        const label = formatTooltipDate(originalValue, isDateAxis);
        const value = point.value ?? '—';
        const seriesName = chart.column || chart.operation || 'Value';

        return `
          <div style="font-weight:600;margin-bottom:6px;color:#0f172a;">
            ${label}
          </div>
          <div style="display:flex;gap:8px;align-items:center;">
            <span style="width:7px;height:7px;border-radius:999px;background:#475569;display:inline-block;"></span>
            <span style="color:#64748b;">${seriesName}</span>
            <strong style="margin-left:auto;color:#0f172a;">${value}</strong>
          </div>
        `;
      },

      axisPointer: {
        type: 'line',
        lineStyle: {
          color: '#cbd5e1',
          width: 1,
          type: 'dashed',
        },
      },
    },

    grid: {
      top: 24,
      right: 20,
      bottom: isDateAxis ? 58 : 50,
      left: 56,
      containLabel: true,
    },

    xAxis: {
      type: 'category',
      data: displayCategories,
      boundaryGap: false,

      axisLabel: {
        color: '#64748b',
        fontSize: 11,
        margin: 12,
        hideOverlap: true,
        rotate: isDateAxis ? 0 : categories.length > 8 ? 35 : 0,
      },

      axisLine: {
        lineStyle: {
          color: '#e7e5e4',
        },
      },

      axisTick: {
        show: false,
      },
    },

    yAxis: {
      type: 'value',

      axisLabel: {
        color: '#64748b',
        fontSize: 11,
        margin: 10,
      },

      axisLine: {
        show: false,
      },

      axisTick: {
        show: false,
      },

      splitLine: {
        lineStyle: {
          color: '#f1f0ef',
          type: 'dashed',
        },
      },
    },

    series: [
      {
        name: chart.column || chart.operation || 'Value',
        type: 'line',
        data: values,

        smooth: 0.25,
        connectNulls: false,

        symbol: 'circle',
        symbolSize: categories.length <= 30 ? 7 : 0,
        showSymbol: categories.length <= 30,

        lineStyle: {
          color: '#475569',
          width: 2.5,
          shadowBlur: 8,
          shadowColor: 'rgba(71, 85, 105, 0.14)',
        },

        itemStyle: {
          color: '#ffffff',
          borderColor: '#475569',
          borderWidth: 2,
        },

        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(71, 85, 105, 0.14)' },
              { offset: 1, color: 'rgba(71, 85, 105, 0.015)' },
            ],
          },
        },

        emphasis: {
          focus: 'series',

          itemStyle: {
            color: '#334155',
            borderColor: '#334155',
            borderWidth: 2,
            shadowBlur: 10,
            shadowColor: 'rgba(51, 65, 85, 0.20)',
          },

          lineStyle: {
            color: '#334155',
            width: 3,
          },
        },

        animationDuration: 900,
        animationDelay: (index) => Math.min(index * 18, 500),
        animationEasing: 'cubicOut',
      },
    ],
  };

  if (rows.length === 0) {
    return (
      <div className='flex h-[300px] items-center justify-center rounded-xl border border-dashed border-stone-200 bg-stone-50/50'>
        <div className='text-center'>
          <p className='text-sm font-medium text-slate-700'>
            No data available
          </p>
          <p className='mt-1 text-xs text-slate-500'>
            There is nothing to plot for this chart.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className='overflow-hidden rounded-xl transition-all duration-300'>
      <ReactECharts
        option={option}
        style={{
          width: '100%',
          height: '300px',
        }}
        opts={{
          renderer: 'canvas',
        }}
        notMerge={true}
        lazyUpdate={true}
      />
    </div>
  );
}

export default LineChart;
