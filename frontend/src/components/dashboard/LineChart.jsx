import ReactECharts from 'echarts-for-react';

function LineChart({ chart, data = [] }) {
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
      bottom: 50,
      left: 56,
      containLabel: true,
    },

    xAxis: {
      type: 'category',
      data: categories,
      boundaryGap: false,

      axisLabel: {
        color: '#64748b',
        fontSize: 11,
        margin: 12,
        rotate: categories.length > 8 ? 35 : 0,
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
        },
      },
    },

    series: [
      {
        name: chart.column || chart.operation || 'Value',
        type: 'line',

        data: values,

        smooth: true,

        connectNulls: false,

        symbol: 'circle',
        symbolSize: 7,

        showSymbol: categories.length <= 20,

        lineStyle: {
          color: '#475569',
          width: 2.5,
        },

        itemStyle: {
          color: '#ffffff',
          borderColor: '#475569',
          borderWidth: 2,
        },

        areaStyle: {
          color: '#94a3b8',
          opacity: 0.08,
        },

        emphasis: {
          focus: 'series',

          itemStyle: {
            color: '#334155',
            borderColor: '#334155',
            borderWidth: 2,
          },

          lineStyle: {
            color: '#334155',
            width: 3,
          },
        },

        animationDuration: 800,
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
