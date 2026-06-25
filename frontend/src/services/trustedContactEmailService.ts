import emailjs from '@emailjs/browser';

const SERVICE_ID = import.meta.env.VITE_EMAILJS_TRUSTED_CONTACTS_SERVICE_ID || '';
const PUBLIC_KEY = import.meta.env.VITE_EMAILJS_TRUSTED_CONTACTS_PUBLIC_KEY || '';
const TEMPLATE_ID = import.meta.env.VITE_EMAILJS_TRUSTED_CONTACTS_TEMPLATE_ID || '';

interface TrustedContactEmailParams {
  toEmail: string;
  toName: string;
  ownerName: string;
  isRegisteredUser: boolean;
}

export async function sendTrustedContactNotificationEmail({
  toEmail,
  toName,
  ownerName,
  isRegisteredUser,
}: TrustedContactEmailParams) {
  if (!SERVICE_ID || !PUBLIC_KEY || !TEMPLATE_ID) {
    console.warn('EmailJS environment variables are not fully configured for trusted contact emails. Email was not sent.');
    return;
  }

  const subject = isRegisteredUser
    ? `${ownerName} added you as a trusted contact on VaultPass`
    : `${ownerName} wants to add you as a trusted contact on VaultPass`;

  const message = isRegisteredUser
    ? `${ownerName} has added you as their trusted contact on VaultPass. Sign in to your account to view this connection.`
    : `${ownerName} has added you as their trusted contact on VaultPass, a secure platform for storing and sharing important documents. Create a free account to view this connection and be ready to assist if they ever need you.`;

  const actionUrl = isRegisteredUser
    ? `${window.location.origin}/login`
    : `${window.location.origin}/signup?email=${encodeURIComponent(toEmail)}`;

  const actionLabel = isRegisteredUser ? 'Sign In to VaultPass' : 'Create Your Account';

  const templateParams = {
    to_email: toEmail,
    to_name: toName,
    owner_name: ownerName,
    subject,
    message,
    action_url: actionUrl,
    action_label: actionLabel,
  };

  return emailjs.send(SERVICE_ID, TEMPLATE_ID, templateParams, PUBLIC_KEY);
}
