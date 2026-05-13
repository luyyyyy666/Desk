export function LearningIsland() {
  return (
    <div className="pointer-events-none absolute bottom-10 right-[150px] h-[310px] w-[390px]" aria-hidden="true">
      <div className="absolute bottom-0 right-0 h-44 w-64 skew-y-[-9deg] rounded-[22px] border-2 border-ink bg-[#8fa34f] shadow-[0_20px_0_#6f5b3d]">
        <div className="absolute inset-5 rounded-[16px] border-2 border-dashed border-ink/70" />
        <div className="absolute left-20 top-12 text-5xl">📘</div>
        <div className="absolute right-12 top-16 text-4xl">✏️</div>
      </div>
      <div className="absolute bottom-20 left-8 h-40 w-44 rotate-[-5deg] rounded-lg border-2 border-ink bg-[#d69a56] shadow-[8px_8px_0_rgba(36,32,21,0.22)]">
        <div className="absolute left-5 top-5 h-28 w-32 rounded-md border-2 border-ink bg-paper-50 p-3 text-sm font-black leading-5">
          错题
          <br />
          再练
          <br />
          计划
        </div>
      </div>
      <div className="absolute bottom-36 right-40 grid h-24 w-24 place-items-center rounded-full border-2 border-ink bg-[#9ac4cf] text-4xl shadow-[5px_5px_0_rgba(36,32,21,0.22)]">
        📐
      </div>
    </div>
  );
}
