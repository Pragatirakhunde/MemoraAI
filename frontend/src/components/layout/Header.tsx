import { Bell, Search, UserCircle } from "lucide-react";

function Header() {
  return (
    <header className="flex h-16 items-center justify-between border-b border-slate-200 bg-white px-6">
      
      {/* Left */}
      <div>
        <h1 className="text-xl font-bold text-slate-800">
          Enterprise Memory Engine
        </h1>

        <p className="text-sm text-slate-500">
          AI Organizational Knowledge Platform
        </p>
      </div>

      {/* Right */}
      <div className="flex items-center gap-4">

        <div className="flex items-center rounded-lg border px-3 py-2">

          <Search size={18} />

          <input
            type="text"
            placeholder="Search..."
            className="ml-2 outline-none"
          />

        </div>

        <Bell size={22} className="cursor-pointer" />

        <UserCircle size={30} className="cursor-pointer" />

      </div>

    </header>
  );
}

export default Header;