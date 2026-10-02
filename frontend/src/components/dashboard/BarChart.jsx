import ReactECharts from 'echarts-for-react';

function BarChart({ chart, data = [] }) {
  const categories = data.map((item) => item[chart.group_by]);

  const values = data.map((item) => item.value);

  const option = {
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#ffffff',
      borderColor: '#e7e5e4',
      borderWidth: 1,
      padding: [10, 12],
      textStyle: {
        color: '#334155',
        fontSize: 12,
      },
      axisPointer: {
        type: 'shadow',
        shadowStyle: {
          color: 'rgba(148, 163, 184, 0.08)',
        },
      },
    },

    grid: {
      top: 24,
      right: 20,
      bottom: 42,
      left: 56,
      containLabel: true,
    },

    xAxis: {
      type: 'category',
      data: categories,
      boundaryGap: true,

      axisLabel: {
        color: '#64748b',
        fontSize: 11,
        margin: 12,
        rotate: categories.length > 6 ? 35 : 0,
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
          type: 'solid',
        },
      },
    },

    series: [
      {
        name: chart.column || chart.operation,
        type: 'bar',
        data: values,

        barMaxWidth: 42,
        barMinHeight: 3,

        itemStyle: {
          color: '#64748b',
          borderRadius: [6, 6, 0, 0],
        },

        emphasis: {
          focus: 'series',

          itemStyle: {
            color: '#475569',
          },
        },

        animationDuration: 700,
        animationEasing: 'cubicOut',
      },
    ],
  };

  return (
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
  );
}

export default BarChart;
