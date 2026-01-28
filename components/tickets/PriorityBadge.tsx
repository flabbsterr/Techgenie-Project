import { TicketPriority } from '@/types/ticket';
import { AlertTriangle, Minus, ChevronDown } from 'lucide-react';

interface PriorityBadgeProps {
  priority: TicketPriority;
}

const priorityConfig = {
  High: {
    className: 'priority-high',
    icon: AlertTriangle,
    label: 'High',
  },
  Medium: {
    className: 'priority-medium',
    icon: Minus,
    label: 'Medium',
  },
  Low: {
    className: 'priority-low',
    icon: ChevronDown,
    label: 'Low',
  },
};

export function PriorityBadge({ priority }: PriorityBadgeProps) {
  const config = priorityConfig[priority];
  const Icon = config.icon;

  return (
    <span className={`status-badge ${config.className}`}>
      <Icon className="mr-1 h-3 w-3" />
      {config.label}
    </span>
  );
}
