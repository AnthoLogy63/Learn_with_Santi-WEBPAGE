import { useState, useEffect } from "react";
import { Outlet, useNavigate } from "react-router-dom";
import { useAppContext } from "@/context/AppContext";
import AdminProfile from "@/components/admin/AdminProfile";
import Logo from "@/media/logo.webp";
import FondoCaja from "@/media/FondoCaja.webp";
import { Menu, X } from "lucide-react";

const AdminLayout = () => {
    // We lift the state here so both Sidebar and Main Content know what's active
    const [activeTab, setActiveTab] = useState("management");
    const [isMenuOpen, setIsMenuOpen] = useState(false);
    const { isAuthenticated, user } = useAppContext();
    const navigate = useNavigate();

    useEffect(() => {
        if (!isAuthenticated) {
            navigate("/", { replace: true });
        } else if (user && !user.is_staff) {
            navigate("/dashboard", { replace: true });
        }
    }, [isAuthenticated, user, navigate]);

    // Close menu when navigation happens (URL changes)
    useEffect(() => {
        setIsMenuOpen(false);
    }, [navigate]);

    if (!isAuthenticated || (user && !user.is_staff)) return null;

    return (
        <div className="flex flex-col lg:flex-row min-h-screen lg:h-screen bg-[#001c4d] lg:overflow-hidden text-white font-inter"
            style={{
                backgroundImage: `url(${FondoCaja})`,
                backgroundSize: "cover",
                backgroundPosition: "center",
                backgroundRepeat: "no-repeat"
            }}
        >
            {/* Mobile Header */}
            <header className="lg:hidden flex items-center justify-between px-6 py-4 bg-white border-b border-gray-200 z-50">
                <img src={Logo} alt="Logo" className="h-10 w-auto object-contain" />
                <button
                    onClick={() => setIsMenuOpen(!isMenuOpen)}
                    className="p-2 text-[#001c4d] hover:bg-slate-100 rounded-lg transition-colors"
                >
                    {isMenuOpen ? <X size={28} /> : <Menu size={28} />}
                </button>
            </header>

            {/* Sidebar Overlay */}
            {isMenuOpen && (
                <div
                    className="lg:hidden fixed inset-0 bg-black/50 backdrop-blur-sm z-40"
                    onClick={() => setIsMenuOpen(false)}
                />
            )}

            {/* Sidebar */}
            <aside className={`
                fixed lg:relative top-[72px] lg:top-0 bottom-0 left-0 z-40
                w-80 lg:w-96 border-r border-white/10 bg-slate-50/95 backdrop-blur-2xl 
                flex-shrink-0 flex flex-col shadow-2xl transition-transform duration-300 ease-in-out
                ${isMenuOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
            `}>
                <div className="w-full bg-white hidden lg:flex items-center justify-center border-b-2 border-gray-300 p-4">
                    <img src={Logo} alt="Logo" className="w-48 h-auto object-contain" />
                </div>

                <div className="flex-1 min-h-0 overflow-y-auto p-4 lg:p-6 lg:px-10">
                    <AdminProfile activeTab={activeTab} setActiveTab={setActiveTab} />
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 lg:overflow-y-auto bg-black/10 backdrop-blur-[2px]">
                {/* We pass the activeTab to the Outlet using context */}
                <Outlet context={{ activeTab }} />
            </main>
        </div>
    );
};

export default AdminLayout;
