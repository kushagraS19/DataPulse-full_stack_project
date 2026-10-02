function ChartCard({ title, chartType, children, onExpand }) {
  return (
    <div className='group relative overflow-hidden rounded-2xl border border-stone-200 bg-white shadow-sm transition-all duration-300 hover:-translate-y-1 hover:border-slate-300 hover:shadow-lg'>
      {/* Top accent */}

      <div className='absolute left-0 top-0 h-0.5 w-0 bg-slate-700 transition-all duration-500 group-hover:w-full' />

      {/* Header */}

      <div className='flex items-start justify-between gap-4 border-b border-stone-100 px-5 py-4'>
        <div className='min-w-0'>
          <h3 className='truncate text-base font-semibold tracking-tight text-slate-900'>
            {title}
          </h3>

          <div className='mt-2 inline-flex items-center rounded-md border border-stone-200 bg-stone-50 px-2 py-1'>
            <span className='text-[10px] font-semibold uppercase tracking-[0.14em] text-slate-500'>
              {chartType}
            </span>
          </div>
        </div>

        {onExpand && (
          <button
            type='button'
            onClick={onExpand}
            className='shrink-0 rounded-lg border border-transparent p-2 text-slate-400 transition-all duration-200 hover:border-stone-200 hover:bg-stone-50 hover:text-slate-700 active:scale-95'
            aria-label={`Expand ${title}`}
          >
            <span className='inline-block text-lg leading-none transition-transform duration-200 group-hover:scale-105'>
              ↗
            </span>
          </button>
        )}
      </div>

      {/* Chart */}

      <div className='min-w-0 p-5'>
        <div className='transition-opacity duration-300 group-hover:opacity-[0.98]'>
          {children}
        </div>
      </div>
    </div>
  );
}

export default ChartCard;
