import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ImportsDashboard } from './imports-dashboard';

describe('ImportsDashboard', () => {
  let component: ImportsDashboard;
  let fixture: ComponentFixture<ImportsDashboard>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ImportsDashboard]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ImportsDashboard);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
