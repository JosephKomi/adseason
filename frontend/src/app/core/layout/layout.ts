import { Component, inject } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { AuthService } from '../services/auth.service';

@Component({
  selector: 'app-layout',
  imports: [RouterOutlet, RouterLink, RouterLinkActive],
  templateUrl: './layout.html',
  styleUrl: './layout.scss',
})
export class Layout {
  auth = inject(AuthService);

  navItems = [
    { path: '/dashboard', icon: 'fas fa-home', label: 'Tableau de bord' },
    { path: '/recommendations', icon: 'fas fa-magic', label: 'Recommandations' },
    { path: '/history', icon: 'fas fa-history', label: 'Historique' },
    { path: '/analytics', icon: 'fas fa-chart-bar', label: 'Analytics' },
  ];
}
