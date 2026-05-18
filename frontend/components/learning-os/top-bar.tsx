import { CircleHelp, Search, UserRound } from "lucide-react";
import { Button } from "@/components/ui/button";

export function TopBar() {
  return (
    <header
      className="flex h-11 items-center border-b-2 border-ink bg-[#ddd8c7] px-4 text-sm text-ink"
      role="banner"
    >
      <div className="mr-7 flex items-center gap-2 font-black">
        <div className="grid h-6 w-7 grid-cols-3 gap-0.5" aria-hidden="true">
          <span className="bg-ink" />
          <span className="bg-ink" />
          <span className="bg-ink" />
          <span className="bg-ink" />
          <span className="bg-ink" />
          <span className="bg-transparent" />
        </div>
        <span>我的师傅</span>
      </div>
      <nav className="flex items-center gap-5 font-bold text-ink/80" aria-label="主菜单">
        <span>生成</span>
        <span>练习</span>
        <span>错题</span>
        <span>知识库</span>
        <span>评估</span>
      </nav>
      <div className="ml-auto flex items-center gap-2">
        <Button variant="default" size="sm">开始任务</Button>
        <button className="grid h-8 w-8 place-items-center rounded-md hover:bg-ink/10" aria-label="搜索">
          <Search size={18} />
        </button>
        <button className="grid h-8 w-8 place-items-center rounded-md hover:bg-ink/10" aria-label="帮助">
          <CircleHelp size={18} />
        </button>
        <button className="grid h-8 w-8 place-items-center rounded-md hover:bg-ink/10" aria-label="账户">
          <UserRound size={19} />
        </button>
      </div>
    </header>
  );
}
