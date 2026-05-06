import { Component, inject, OnInit, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { ApiService } from '../../core/services/api.service';
import { AuthService } from '../../core/services/auth.service';
import { Dataset } from '../../core/models/dataset.model';
import { Recommendation } from '../../core/models/recommendation.model';

@Component({
  selector: 'app-dashboard',
  imports: [RouterLink],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.scss',
})
export class Dashboard implements OnInit {
  private api = inject(ApiService);
  auth = inject(AuthService);

  datasets = signal<Dataset[]>([]);
  recommendations = signal<Recommendation[]>([]);
  loading = signal(true);

  ngOnInit() {
    this.api.get<Dataset[]>('/api/datasets').subscribe({
      next: (d) => this.datasets.set(d),
    });
    this.api.get<Recommendation[]>('/api/recommendations').subscribe({
      next: (r) => {
        this.recommendations.set(r);
        this.loading.set(false);
      },
      error: () => this.loading.set(false),
    });
  }

  get processedDatasets() {
    return this.datasets().filter(d => d.status === 'processed').length;
  }

  get totalRows() {
    return this.datasets().reduce((sum, d) => sum + (d.row_count ?? 0), 0);
  }

  formatDate(date: string) {
    return new Date(date).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric' });
  }
}
