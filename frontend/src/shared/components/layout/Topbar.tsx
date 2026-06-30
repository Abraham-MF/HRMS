import { Menu, Bell } from "lucide-react";
import { useAuthStore } from "@/modules/auth/store/authStore";

interface TopbarProps {
  onMenuClick: () => void;
}

export default function Topbar({ onMenuClick }: TopbarProps) {
  const { user } = useAuthStore();

  return (
    <header className="h-14 bg-[#1c1c21] border-b border-zinc-800/60 flex items-center justify-between px-5 shrink-0">
      <button
        onClick={onMenuClick}
        className="p-1.5 rounded-lg text-zinc-500 hover:bg-zinc-800 hover:text-white transition-colors lg:hidden"
        aria-label="Abrir menú"
      >
        <Menu size={20} />
      </button>

      <div className="flex-1 lg:flex-none" />

      <div className="flex items-center gap-3">
        <button className="p-1.5 rounded-lg text-zinc-500 hover:bg-zinc-800 hover:text-white transition-colors relative">
          <Bell size={18} />
          <span className="absolute top-1 right-1 w-2 h-2 bg-purple-500 rounded-full" />
        </button>

        {user && (
          <div className="flex items-center gap-2.5 pl-3 border-l border-zinc-800">
            <div className="w-7 h-7 bg-gradient-to-br from-purple-600 to-purple-900
              rounded-full flex items-center justify-center text-white font-semibold text-xs">
              {user.username?.[0]?.toUpperCase() ?? 'U'}
            </div>
            <div className="hidden sm:block text-right">
              <p className="text-sm font-medium text-white leading-none">{user.username}</p>
              <p className="text-xs text-purple-400 mt-0.5">{user.role}</p>
            </div>
          </div>
        )}
      </div>
    </header>
  );
}
