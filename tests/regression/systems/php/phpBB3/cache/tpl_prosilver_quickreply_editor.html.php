<?php if (!defined('IN_PHPBB')) exit; ?><script type="text/javascript">
// <![CDATA[
	function hide_qr(show)
	{
		dE('qr_editor_div');
		dE('qr_showeditor_div');
		if (show && document.getElementById('qr_editor_div').style.display != 'none')
		{
			document.getElementsByName('message')[0].focus();
		}
		return true;
	}


	function init_qr()
	{
		dE('qr_showeditor_div');
		return true;
	}
	onload_functions.push('init_qr();');
	// ]]>
</script>
<noscript>
	<form method="post" action="<?php echo (isset($this->_rootref['U_QR_ACTION'])) ? $this->_rootref['U_QR_ACTION'] : ''; ?>">
		<div class="panel" id="qr_ns_editor_div">
			<div class="inner"><span class="corners-top"><span></span></span>
					<h2><?php echo ((isset($this->_rootref['L_QUICKREPLY'])) ? $this->_rootref['L_QUICKREPLY'] : ((isset($user->lang['QUICKREPLY'])) ? $user->lang['QUICKREPLY'] : '{ QUICKREPLY }')); ?></h2>
					<fieldset class="fields1">
						<dl style="clear: left;">
							<dt><label for="subject"><?php echo ((isset($this->_rootref['L_SUBJECT'])) ? $this->_rootref['L_SUBJECT'] : ((isset($user->lang['SUBJECT'])) ? $user->lang['SUBJECT'] : '{ SUBJECT }')); ?>:</label></dt>
							<dd><input type="text" name="subject" id="subject-ns" size="45" maxlength="64" tabindex="2" value="<?php echo (isset($this->_rootref['SUBJECT'])) ? $this->_rootref['SUBJECT'] : ''; ?>" class="inputbox autowidth" /></dd>
						</dl>
					<div id="message-box-ns">
						<textarea style="height: 9em;" name="message" rows="7" cols="76" tabindex="3" class="inputbox"></textarea>
					</div>
					</fieldset>
					<fieldset class="submit-buttons">
						<?php echo (isset($this->_rootref['S_FORM_TOKEN'])) ? $this->_rootref['S_FORM_TOKEN'] : ''; ?>

						<?php echo (isset($this->_rootref['QR_HIDDEN_FIELDS'])) ? $this->_rootref['QR_HIDDEN_FIELDS'] : ''; ?>

						<input type="submit" accesskey="s" tabindex="6" name="post" value="<?php echo ((isset($this->_rootref['L_SUBMIT'])) ? $this->_rootref['L_SUBMIT'] : ((isset($user->lang['SUBMIT'])) ? $user->lang['SUBMIT'] : '{ SUBMIT }')); ?>" class="button1" />&nbsp;
						<input type="submit" accesskey="f" tabindex="7" name="full_editor" value="<?php echo ((isset($this->_rootref['L_FULL_EDITOR'])) ? $this->_rootref['L_FULL_EDITOR'] : ((isset($user->lang['FULL_EDITOR'])) ? $user->lang['FULL_EDITOR'] : '{ FULL_EDITOR }')); ?>" class="button2" />&nbsp;
					</fieldset>
			<span class="corners-bottom"><span></span></span></div>
		</div>
	</form>
</noscript>
<form method="post" action="<?php echo (isset($this->_rootref['U_QR_ACTION'])) ? $this->_rootref['U_QR_ACTION'] : ''; ?>">
	<div class="panel" style="display: none" id="qr_editor_div">
		<div class="inner"><span class="corners-top"><span></span></span>
				<h2><?php echo ((isset($this->_rootref['L_QUICKREPLY'])) ? $this->_rootref['L_QUICKREPLY'] : ((isset($user->lang['QUICKREPLY'])) ? $user->lang['QUICKREPLY'] : '{ QUICKREPLY }')); ?></h2>
				<fieldset class="fields1">
					<dl style="clear: left;">
						<dt><label for="subject"><?php echo ((isset($this->_rootref['L_SUBJECT'])) ? $this->_rootref['L_SUBJECT'] : ((isset($user->lang['SUBJECT'])) ? $user->lang['SUBJECT'] : '{ SUBJECT }')); ?>:</label></dt>
						<dd><input type="text" name="subject" id="subject" size="45" maxlength="64" tabindex="2" value="<?php echo (isset($this->_rootref['SUBJECT'])) ? $this->_rootref['SUBJECT'] : ''; ?>" class="inputbox autowidth" /></dd>
					</dl>
				<div id="message-box">
					<textarea style="height: 9em;" name="message" rows="7" cols="76" tabindex="3" class="inputbox"></textarea>
				</div>
				</fieldset>
				<fieldset class="submit-buttons">
					<?php echo (isset($this->_rootref['S_FORM_TOKEN'])) ? $this->_rootref['S_FORM_TOKEN'] : ''; ?>

					<?php echo (isset($this->_rootref['QR_HIDDEN_FIELDS'])) ? $this->_rootref['QR_HIDDEN_FIELDS'] : ''; ?>

					<input type="submit" accesskey="s" tabindex="6" name="post" value="<?php echo ((isset($this->_rootref['L_SUBMIT'])) ? $this->_rootref['L_SUBMIT'] : ((isset($user->lang['SUBMIT'])) ? $user->lang['SUBMIT'] : '{ SUBMIT }')); ?>" class="button1" />&nbsp;
					<input type="submit" accesskey="f" tabindex="7" name="full_editor" value="<?php echo ((isset($this->_rootref['L_FULL_EDITOR'])) ? $this->_rootref['L_FULL_EDITOR'] : ((isset($user->lang['FULL_EDITOR'])) ? $user->lang['FULL_EDITOR'] : '{ FULL_EDITOR }')); ?>" class="button2" />&nbsp;
				</fieldset>
				<a href="" class="right-box up" onclick="hide_qr(false); return false;" title="<?php echo ((isset($this->_rootref['L_COLLAPSE_QR'])) ? $this->_rootref['L_COLLAPSE_QR'] : ((isset($user->lang['COLLAPSE_QR'])) ? $user->lang['COLLAPSE_QR'] : '{ COLLAPSE_QR }')); ?>"><?php echo ((isset($this->_rootref['L_COLLAPSE_QR'])) ? $this->_rootref['L_COLLAPSE_QR'] : ((isset($user->lang['COLLAPSE_QR'])) ? $user->lang['COLLAPSE_QR'] : '{ COLLAPSE_QR }')); ?></a>
		<span class="corners-bottom"><span></span></span></div>
	</div>
	<div class="panel" style="display: none" id="qr_showeditor_div" >
		<div class="inner"><span class="corners-top"><span></span></span>

			<div class="content">
				<fieldset class="submit-buttons">
					<input type="submit" name="show_qr" tabindex="1" class="button2" value="<?php echo ((isset($this->_rootref['L_SHOW_QR'])) ? $this->_rootref['L_SHOW_QR'] : ((isset($user->lang['SHOW_QR'])) ? $user->lang['SHOW_QR'] : '{ SHOW_QR }')); ?>" onclick="hide_qr(true);return false;"/>
				</fieldset>
			</div>
		<span class="corners-bottom"><span></span></span></div>
	</div>
</form>