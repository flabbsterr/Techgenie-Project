import { NavLink } from '@/components/NavLink';
import { Headphones, TicketPlus, List, LayoutDashboard, LogOut } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/ui/button';
import { useNavigate } from 'react-router-dom';
import { useToast } from '@/hooks/use-toast';

export function Header() {
  const { user, signOut } = useAuth();
  const navigate = useNavigate();
  const { toast } = useToast();

  const handleSignOut = async () => {
    await signOut();
    toast({
      title: 'Signed out',
      description: 'You have been signed out successfully.',
    });
    navigate('/auth');
  };

  return (
    <header className="border-b bg-card">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary">
              <Headphones className="h-5 w-5 text-primary-foreground" />
            </div>
            <div>
              <h1 className="text-lg font-semibold text-foreground">IT Support Portal</h1>
              <p className="text-xs text-muted-foreground">Ticket Management System</p>
            </div>
          </div>
          
          <nav className="flex items-center gap-1">
            <NavLink
              to="/log"
              className="flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground"
              activeClassName="bg-secondary text-foreground"
            >
              <TicketPlus className="h-4 w-4" />
              Log Ticket
            </NavLink>
            <NavLink
              to="/my-tickets"
              className="flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground"
              activeClassName="bg-secondary text-foreground"
            >
              <List className="h-4 w-4" />
              My Tickets
            </NavLink>
            <NavLink
              to="/it-dashboard"
              className="flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground"
              activeClassName="bg-secondary text-foreground"
            >
              <LayoutDashboard className="h-4 w-4" />
              IT Dashboard
            </NavLink>
            
            {user && (
              <Button
                variant="ghost"
                size="sm"
                onClick={handleSignOut}
                className="ml-2 text-muted-foreground hover:text-destructive"
              >
                <LogOut className="h-4 w-4 mr-1" />
                Sign Out
              </Button>
            )}
          </nav>
        </div>
      </div>
    </header>
  );
}
