import { useNavigate } from 'react-router-dom';

function Landing() {
  const navigate = useNavigate();

  const features = [
    {
      number: '01',
      title: 'Upload your data',
      description:
        'Bring your CSV files into one workspace and get your data ready for analysis.',
    },
    {
      number: '02',
      title: 'Explore the patterns',
      description:
        'Review automatically generated charts and key metrics without building every report manually.',
    },
    {
      number: '03',
      title: 'Make sense of it',
      description:
        'Use clear insights to understand trends, compare categories, and spot unusual values.',
    },
  ];

  return (
    <main className='min-h-screen overflow-hidden bg-[#f7f7f4] text-slate-950'>
      <header className='relative z-10 mx-auto flex w-full max-w-7xl items-center justify-between px-5 py-5 sm:px-8 lg:px-12'>
        <button
          type='button'
          onClick={() => navigate('/')}
          className='flex items-center gap-3'
          aria-label='DataPulse home'
        >
          <span className='flex h-10 w-10 items-center justify-center rounded-xl bg-slate-950 text-sm font-black text-white shadow-sm'>
            D
          </span>
          <span className='text-lg font-bold tracking-tight'>DataPulse</span>
        </button>

        <nav
          className='flex items-center gap-3 sm:gap-5'
          aria-label='Main navigation'
        >
          <button
            type='button'
            onClick={() => navigate('/login')}
            className='rounded-xl px-3 py-2 text-sm font-semibold text-slate-600 transition hover:text-slate-950 sm:px-4'
          >
            Log in
          </button>
          <button
            type='button'
            onClick={() => navigate('/register')}
            className='rounded-xl bg-slate-950 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:-translate-y-0.5 hover:bg-slate-800 sm:px-5'
          >
            Get started <span aria-hidden='true'>→</span>
          </button>
        </nav>
      </header>

      <section className='relative mx-auto grid w-full max-w-7xl items-center gap-14 px-5 pb-20 pt-12 sm:px-8 sm:pb-24 sm:pt-16 lg:grid-cols-[1.02fr_0.98fr] lg:gap-12 lg:px-12 lg:pb-28 lg:pt-20'>
        <div className='pointer-events-none absolute -left-40 top-12 h-80 w-80 rounded-full bg-stone-200/70 blur-3xl' />
        <div className='pointer-events-none absolute right-0 top-0 h-72 w-72 rounded-full bg-slate-200/60 blur-3xl' />

        <div className='relative z-10'>
          <div className='inline-flex items-center gap-2 rounded-full border border-stone-200 bg-white/80 px-3.5 py-2 text-xs font-semibold text-slate-600 shadow-sm'>
            <span className='h-2 w-2 rounded-full bg-emerald-500' />A clearer
            view of your data
          </div>

          <h1 className='mt-7 max-w-2xl text-4xl font-bold leading-[1.08] tracking-tight sm:text-5xl lg:text-6xl'>
            Your data has a story.
            <span className='mt-2 block text-slate-500'>
              Find what it’s telling you.
            </span>
          </h1>

          <p className='mt-6 max-w-xl text-base leading-7 text-slate-600 sm:text-lg sm:leading-8'>
            DataPulse turns raw CSV data into useful charts, key metrics, and
            understandable insights—so you can spend less time sorting numbers
            and more time making informed decisions.
          </p>

          <div className='mt-8 flex flex-col gap-3 sm:flex-row'>
            <button
              type='button'
              onClick={() => navigate('/register')}
              className='inline-flex h-12 items-center justify-center gap-2 rounded-xl bg-slate-950 px-6 text-sm font-semibold text-white shadow-lg shadow-slate-900/10 transition hover:-translate-y-0.5 hover:bg-slate-800'
            >
              Get started for free <span aria-hidden='true'>→</span>
            </button>
            <button
              type='button'
              onClick={() => navigate('/login')}
              className='inline-flex h-12 items-center justify-center rounded-xl border border-stone-300 bg-white/80 px-6 text-sm font-semibold text-slate-700 transition hover:border-slate-400 hover:bg-white'
            >
              I already have an account
            </button>
          </div>

          <div className='mt-8 flex flex-wrap items-center gap-x-6 gap-y-2 text-xs font-medium text-slate-500'>
            <span className='inline-flex items-center gap-2'>
              <span className='text-emerald-600'>✓</span> CSV-based analysis
            </span>
            <span className='inline-flex items-center gap-2'>
              <span className='text-emerald-600'>✓</span> Auto-generated
              dashboards
            </span>
            <span className='inline-flex items-center gap-2'>
              <span className='text-emerald-600'>✓</span> Clear visual insights
            </span>
          </div>
        </div>

        <div className='relative z-10 mx-auto w-full max-w-xl'>
          <div className='absolute -inset-4 rounded-[2rem] bg-white/70 blur-2xl' />
          <div className='relative rounded-[1.7rem] border border-stone-200/90 bg-white p-4 shadow-[0_28px_90px_rgba(15,23,42,0.12)] sm:p-6'>
            <div className='flex items-start justify-between gap-4 border-b border-stone-100 pb-5'>
              <div>
                <p className='text-xs font-semibold uppercase tracking-[0.16em] text-slate-400'>
                  Dashboard preview
                </p>
                <h2 className='mt-1.5 text-lg font-bold tracking-tight'>
                  Business overview
                </h2>
                <p className='mt-1 text-xs text-slate-500'>
                  A sample view of your data
                </p>
              </div>
              <span className='rounded-lg border border-stone-200 bg-stone-50 px-3 py-1.5 text-xs font-semibold text-slate-500'>
                All data
              </span>
            </div>

            <div className='mt-5 grid grid-cols-3 gap-3'>
              {[
                { label: 'Total records', value: '10,240', change: '+12.8%' },
                { label: 'Avg. value', value: '₹4,820', change: '+6.4%' },
                { label: 'Categories', value: '18', change: 'Tracked' },
              ].map((metric) => (
                <div
                  key={metric.label}
                  className='min-w-0 rounded-2xl border border-stone-100 bg-[#fafaf8] p-3 sm:p-4'
                >
                  <p className='truncate text-[10px] font-medium text-slate-500 sm:text-xs'>
                    {metric.label}
                  </p>
                  <p className='mt-2 truncate text-lg font-bold tracking-tight sm:text-2xl'>
                    {metric.value}
                  </p>
                  <p className='mt-1 text-[10px] font-semibold text-emerald-700 sm:text-xs'>
                    {metric.change}
                  </p>
                </div>
              ))}
            </div>

            <div className='mt-4 grid gap-4 sm:grid-cols-[1.4fr_0.8fr]'>
              <div className='rounded-2xl border border-stone-100 p-4'>
                <div className='flex items-center justify-between gap-2'>
                  <div>
                    <p className='text-xs font-semibold text-slate-800'>
                      Performance trend
                    </p>
                    <p className='mt-1 text-[10px] text-slate-400'>
                      Illustrative monthly data
                    </p>
                  </div>
                  <span className='text-xs font-semibold text-slate-500'>
                    ↗
                  </span>
                </div>
                <div className='relative mt-5 h-32'>
                  <div className='absolute inset-0 flex flex-col justify-between'>
                    <div className='border-t border-dashed border-stone-200' />
                    <div className='border-t border-dashed border-stone-200' />
                    <div className='border-t border-dashed border-stone-200' />
                    <div className='border-t border-dashed border-stone-200' />
                  </div>
                  <svg
                    viewBox='0 0 320 120'
                    className='absolute inset-0 h-full w-full overflow-visible'
                    role='img'
                    aria-label='Illustrative upward performance trend'
                  >
                    <defs>
                      <linearGradient
                        id='trendFill'
                        x1='0'
                        x2='0'
                        y1='0'
                        y2='1'
                      >
                        <stop
                          offset='0%'
                          stopColor='#64748b'
                          stopOpacity='0.22'
                        />
                        <stop
                          offset='100%'
                          stopColor='#64748b'
                          stopOpacity='0'
                        />
                      </linearGradient>
                    </defs>
                    <path
                      d='M0 96 C25 88 30 78 55 83 S95 68 120 74 S158 45 185 56 S225 35 245 42 S285 18 320 12 L320 120 L0 120 Z'
                      fill='url(#trendFill)'
                    />
                    <path
                      d='M0 96 C25 88 30 78 55 83 S95 68 120 74 S158 45 185 56 S225 35 245 42 S285 18 320 12'
                      fill='none'
                      stroke='#334155'
                      strokeWidth='3'
                      strokeLinecap='round'
                    />
                    <circle
                      cx='320'
                      cy='12'
                      r='4.5'
                      fill='#334155'
                      stroke='white'
                      strokeWidth='2'
                    />
                  </svg>
                </div>
                <div className='mt-2 flex justify-between text-[10px] text-slate-400'>
                  <span>Jan</span>
                  <span>Mar</span>
                  <span>May</span>
                  <span>Jul</span>
                  <span>Sep</span>
                  <span>Nov</span>
                </div>
              </div>

              <div className='rounded-2xl border border-stone-100 p-4'>
                <p className='text-xs font-semibold text-slate-800'>
                  Category mix
                </p>
                <p className='mt-1 text-[10px] text-slate-400'>
                  Illustrative distribution
                </p>
                <div className='flex justify-center py-4'>
                  <div
                    className='flex h-28 w-28 items-center justify-center rounded-full'
                    style={{
                      background:
                        'conic-gradient(#334155 0 42%, #94a3b8 42% 70%, #cbd5e1 70% 88%, #e7e5e4 88% 100%)',
                    }}
                  >
                    <div className='flex h-[4.2rem] w-[4.2rem] flex-col items-center justify-center rounded-full bg-white'>
                      <span className='text-lg font-bold'>100%</span>
                      <span className='text-[9px] text-slate-400'>total</span>
                    </div>
                  </div>
                </div>
                <div className='space-y-2'>
                  {[
                    ['Primary', '42%', '#334155'],
                    ['Secondary', '28%', '#94a3b8'],
                    ['Other', '30%', '#d6d3d1'],
                  ].map(([label, value, color]) => (
                    <div
                      key={label}
                      className='flex items-center justify-between gap-2 text-[10px]'
                    >
                      <span className='flex items-center gap-2 text-slate-500'>
                        <span
                          className='h-2 w-2 rounded-sm'
                          style={{ backgroundColor: color }}
                        />
                        {label}
                      </span>
                      <span className='font-semibold text-slate-700'>
                        {value}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className='mt-4 flex items-start gap-3 rounded-2xl border border-emerald-100 bg-emerald-50/70 p-4'>
              <span className='flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-white text-sm text-emerald-700 shadow-sm'>
                ↗
              </span>
              <div>
                <p className='text-xs font-bold text-slate-800'>
                  Insight at a glance
                </p>
                <p className='mt-1 text-xs leading-5 text-slate-600'>
                  Spot trends and compare values from a single, organized view.
                </p>
              </div>
            </div>
            <p className='mt-3 text-center text-[10px] text-slate-400'>
              Illustrative preview — not live user data
            </p>
          </div>
        </div>
      </section>

      <section className='border-y border-stone-200/80 bg-white/70'>
        <div className='mx-auto max-w-7xl px-5 py-16 sm:px-8 lg:px-12 lg:py-20'>
          <div className='max-w-2xl'>
            <p className='text-xs font-bold uppercase tracking-[0.18em] text-slate-400'>
              From file to findings
            </p>
            <h2 className='mt-3 text-3xl font-bold tracking-tight sm:text-4xl'>
              Analytics, without the busywork.
            </h2>
            <p className='mt-4 text-sm leading-7 text-slate-600 sm:text-base'>
              Start with the data you already have. DataPulse helps organize it
              into a dashboard you can explore.
            </p>
          </div>

          <div className='mt-10 grid gap-4 md:grid-cols-3'>
            {features.map((feature) => (
              <article
                key={feature.number}
                className='rounded-2xl border border-stone-200 bg-white p-6 transition hover:-translate-y-1 hover:shadow-lg hover:shadow-slate-900/5 sm:p-7'
              >
                <p className='text-xs font-bold tracking-[0.15em] text-slate-400'>
                  {feature.number}
                </p>
                <h3 className='mt-5 text-lg font-bold'>{feature.title}</h3>
                <p className='mt-3 text-sm leading-6 text-slate-600'>
                  {feature.description}
                </p>
              </article>
            ))}
          </div>

          <div className='mt-12 flex flex-col items-start justify-between gap-5 rounded-3xl bg-slate-950 px-6 py-8 text-white sm:px-9 sm:py-10 md:flex-row md:items-center'>
            <div>
              <h3 className='text-2xl font-bold tracking-tight'>
                Ready to explore your data?
              </h3>
              <p className='mt-2 max-w-xl text-sm leading-6 text-slate-400'>
                Create an account to start organizing datasets and generating
                dashboards.
              </p>
            </div>
            <button
              type='button'
              onClick={() => navigate('/register')}
              className='inline-flex h-12 shrink-0 items-center justify-center gap-2 rounded-xl bg-white px-5 text-sm font-semibold text-slate-950 transition hover:bg-stone-200'
            >
              Create your account <span aria-hidden='true'>→</span>
            </button>
          </div>
        </div>
      </section>

      <footer className='mx-auto flex max-w-7xl flex-col gap-3 px-5 py-7 text-xs text-slate-500 sm:flex-row sm:items-center sm:justify-between sm:px-8 lg:px-12'>
        <div className='flex items-center gap-2'>
          <span className='flex h-7 w-7 items-center justify-center rounded-lg bg-slate-950 text-[10px] font-black text-white'>
            D
          </span>
          <span className='font-semibold text-slate-700'>DataPulse</span>
          <span>· Make your data useful.</span>
        </div>
        <div>© {new Date().getFullYear()} DataPulse</div>
      </footer>
    </main>
  );
}

export default Landing;
