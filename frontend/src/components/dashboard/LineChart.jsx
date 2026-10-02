import ReactECharts from 'echarts-for-react';

function LineChart({ chart, data = [] }) {
  const categories = data.map((item) => item[chart.group_by]);

  const values = data.map((item) => item.value);

  const option = {
    tooltip: {
      trigger: 'axis',
    },

    grid: {
      top: 20,
      right: 20,
      bottom: 40,
      left: 60,
      containLabel: true,
    },

    xAxis: {
      type: 'category',
      data: categories,
      boundaryGap: false,
      axisLabel: {
        color: '#64748b',
      },
      axisLine: {
        lineStyle: {
          color: '#e2e8f0',
        },
      },
    },

    yAxis: {
      type: 'value',
      axisLabel: {
        color: '#64748b',
      },
      splitLine: {
        lineStyle: {
          color: '#e2e8f0',
          type: 'dashed',
        },
      },
    },

    series: [
      {
        name: chart.column || chart.operation,
        type: 'line',
        data: values,

        smooth: true,

        symbol: 'circle',
        symbolSize: 7,

        lineStyle: {
          width: 3,
        },

        areaStyle: {
          opacity: 0.08,
        },

        emphasis: {
          focus: 'series',
        },

        animationDuration: 900,
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

export default LineChart;
