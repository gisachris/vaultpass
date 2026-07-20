import emailjs from '@emailjs/browser';

const SERVICE_ID = import.meta.env.VITE_EMAILJS_SERVICE_ID || '';
const PUBLIC_KEY = import.meta.env.VITE_EMAILJS_PUBLIC_KEY || '';

export async function sendVerificationEmail(
  toEmail: string,
  toName: string,
  verificationLink: string
) {
  const templateId = import.meta.env.VITE_EMAILJS_VERIFICATION_TEMPLATE_ID || '';
  if (!SERVICE_ID || !PUBLIC_KEY || !templateId) {
    console.warn('EmailJS environment variables are not fully configured. Email was not sent.');
    return;
  }
  const templateParams = {
    to_email: toEmail,
    to_name: toName,
    verification_link: verificationLink,
  };
  return emailjs.send(SERVICE_ID, templateId, templateParams, PUBLIC_KEY);
}

export async function sendPasswordResetEmail(
  toEmail: string,
  resetLink: string
) {
  const templateId = import.meta.env.VITE_EMAILJS_RESET_TEMPLATE_ID || '';
  if (!SERVICE_ID || !PUBLIC_KEY || !templateId) {
    console.warn('EmailJS environment variables are not fully configured. Email was not sent.');
    return;
  }
  const templateParams = {
    to_email: toEmail,
    reset_link: resetLink,
  };
  return emailjs.send(SERVICE_ID, templateId, templateParams, PUBLIC_KEY);
}
