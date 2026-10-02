import ReactECharts from 'echarts-for-react';

function BarChart({ chart, data = [] }) {
  const categories = data.map((item) => item[chart.group_by]);

  const values = data.map((item) => item.value);

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow',
      },
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
      axisLabel: {
        color: '#64748b',
        rotate: categories.length > 6 ? 35 : 0,
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
        type: 'bar',
        data: values,
        barMaxWidth: 50,

        itemStyle: {
          borderRadius: [8, 8, 0, 0],
        },

        emphasis: {
          focus: 'series',
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

export default BarChart;
