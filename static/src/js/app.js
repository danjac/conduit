import '@hotwired/turbo';

import { Application } from 'stimulus';

import ConfirmController from './controllers/confirm-controller';
import LinkController from './controllers/link-controller';
import SlugifyController from './controllers/slugify-controller';
import ToastController from './controllers/toast-controller';
import ToggleController from './controllers/toggle-controller';

// Stimulus setup
const application = Application.start();

application.register('confirm', ConfirmController);
application.register('link', LinkController);
application.register('slugify', SlugifyController);
application.register('toast', ToastController);
application.register('toggle', ToggleController);
