function ChartCard({ title, chartType, children, onExpand }) {
  return (
    <div className='group relative overflow-hidden rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition-all duration-300 hover:-translate-y-1 hover:shadow-xl dark:border-slate-800 dark:bg-slate-900'>
      <div className='mb-4 flex items-start justify-between gap-4'>
        <div>
          <h3 className='text-base font-semibold text-slate-900 dark:text-white'>
            {title}
          </h3>

          <p className='mt-1 text-xs capitalize text-slate-500 dark:text-slate-400'>
            {chartType} chart
          </p>
        </div>

        <button
          type='button'
          onClick={onExpand}
          className='rounded-lg p-2 text-slate-400 transition-colors hover:bg-slate-100 hover:text-slate-900 dark:hover:bg-slate-800 dark:hover:text-white'
          aria-label={`Expand ${title}`}
        >
          ⛶
        </button>
      </div>

      <div className='min-h-[280px] w-full'>{children}</div>
    </div>
  );
}

export default ChartCard;
