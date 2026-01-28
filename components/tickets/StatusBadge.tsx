import { TicketStatus } from '@/types/ticket';
import { Circle, Clock, CheckCircle2 } from 'lucide-react';

interface StatusBadgeProps {
  status: TicketStatus;
}

const statusConfig = {
  Open: {
    className: 'status-open',
    icon: Circle,
    label: 'Open',
  },
  'In Progress': {
    className: 'status-progress',
    icon: Clock,
    label: 'In Progress',
  },
  Closed: {
    className: 'status-closed',
    icon: CheckCircle2,
    label: 'Closed',
  },
};

export function StatusBadge({ status }: StatusBadgeProps) {
  const config = statusConfig[status];
  const Icon = config.icon;

  return (
    <span className={`status-badge ${config.className}`}>
      <Icon className="mr-1 h-3 w-3" />
      {config.label}
    </span>
  );
}
