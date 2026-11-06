# -*- coding: utf-8 -*-
import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), 'war_room_blocks'))

from block1_imports import get_block1
from block2_tabs import get_template_tabs
from block2_modals import get_template_modals
from block3_styles import get_styles
from block4_class import get_class_body

OUT_PATH = r'frontend/src/app/features/candidates/candidate-war-room.page.ts'

block1 = get_block1()
tabs = get_template_tabs()
modals = get_template_modals()
styles = get_styles()
class_body = get_class_body()

template = f"""{tabs}
{modals}"""

full_content = f"""{block1}

@Component({{
  selector: 'eems-candidate-war-room',
  imports: [CommonModule, DatePipe, DecimalPipe, FormsModule, RouterLink],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `{template}
  `,
  styles: [`{styles}
  `]
}})
{class_body}
"""

with open(OUT_PATH, 'w', encoding='utf-8') as f:
    f.write(full_content)

print(f"Successfully assembled {OUT_PATH}! Total characters: {len(full_content)}")

