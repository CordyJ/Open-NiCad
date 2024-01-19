<?php if (!defined('IN_PHPBB')) exit; ?>Subject: phpBB installed

Congratulations,

You have successfully installed phpBB on your server.

This e-mail contains important information regarding your installation and should be kept for reference. Your password has been securely stored in our database and cannot be retrieved. In the event that it is forgotten, you will be able to reset it using the email address associated with your account.

----------------------------
Username: <?php echo (isset($this->_rootref['USERNAME'])) ? $this->_rootref['USERNAME'] : ''; ?>


Board URL: <?php echo (isset($this->_rootref['U_BOARD'])) ? $this->_rootref['U_BOARD'] : ''; ?>

----------------------------

Useful information regarding the phpBB software can be found in the docs folder of your installation and on phpBB.com's support page - https://www.phpbb.com/support/

In order to keep your board safe and secure, we highly recommended keeping current with software releases. For your convenience, a mailing list is available at the page referenced above.

<?php echo (isset($this->_rootref['EMAIL_SIG'])) ? $this->_rootref['EMAIL_SIG'] : ''; ?>