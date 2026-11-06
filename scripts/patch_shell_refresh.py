with open('frontend/src/app/layout/shell/shell.component.ts', 'r', encoding='utf-8') as f:
    c = f.read()

target1 = "import {RouterLink,RouterLinkActive,RouterOutlet} from '@angular/router';"
repl1 = "import {NavigationEnd,Router,RouterLink,RouterLinkActive,RouterOutlet} from '@angular/router';\nimport {filter} from 'rxjs';"

target2 = """  ngOnInit() {
    if (this.auth.authenticated()) {
      this.loadCandidates();
    }
  }"""

repl2 = """  private readonly router = inject(Router);

  ngOnInit() {
    if (this.auth.authenticated()) {
      this.loadCandidates();
    }
    this.router.events.pipe(
      filter(e => e instanceof NavigationEnd)
    ).subscribe(() => {
      if (this.auth.authenticated()) {
        this.loadCandidates();
      }
    });
  }"""

if target1 in c and target2 in c:
    c = c.replace(target1, repl1).replace(target2, repl2)
    with open('frontend/src/app/layout/shell/shell.component.ts', 'w', encoding='utf-8') as f:
        f.write(c)
    print("shell.component.ts updated successfully!")
else:
    print("Targets not found!")

