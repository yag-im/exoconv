# Exo collection converter

Converts exo games collections into yag ports.

# Usage

1. Generate a state map between exo and yag collections:

    exoconv ready

2. Generate fake installers and copy app content into yag ports:

    exoconv steady

3. Push generated artifacts to prod:

    exoconv go
