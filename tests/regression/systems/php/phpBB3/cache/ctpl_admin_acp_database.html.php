<?php if (!defined('IN_PHPBB')) exit; $this->_tpl_include('overall_header.html'); ?>


<a name="maincontent"></a>

<?php if ($this->_rootref['MODE'] == ('restore')) {  ?>

	<h1><?php echo ((isset($this->_rootref['L_ACP_RESTORE'])) ? $this->_rootref['L_ACP_RESTORE'] : ((isset($user->lang['ACP_RESTORE'])) ? $user->lang['ACP_RESTORE'] : '{ ACP_RESTORE }')); ?></h1>

	<p><?php echo ((isset($this->_rootref['L_ACP_RESTORE_EXPLAIN'])) ? $this->_rootref['L_ACP_RESTORE_EXPLAIN'] : ((isset($user->lang['ACP_RESTORE_EXPLAIN'])) ? $user->lang['ACP_RESTORE_EXPLAIN'] : '{ ACP_RESTORE_EXPLAIN }')); ?></p>

	<?php if (sizeof($this->_tpldata['files'])) {  ?>

	<form id="acp_backup" method="post" action="<?php echo (isset($this->_rootref['U_ACTION'])) ? $this->_rootref['U_ACTION'] : ''; ?>">

	<fieldset>
		<legend><?php echo ((isset($this->_rootref['L_RESTORE_OPTIONS'])) ? $this->_rootref['L_RESTORE_OPTIONS'] : ((isset($user->lang['RESTORE_OPTIONS'])) ? $user->lang['RESTORE_OPTIONS'] : '{ RESTORE_OPTIONS }')); ?></legend>
	<dl>
		<dt><label for="file"><?php echo ((isset($this->_rootref['L_SELECT_FILE'])) ? $this->_rootref['L_SELECT_FILE'] : ((isset($user->lang['SELECT_FILE'])) ? $user->lang['SELECT_FILE'] : '{ SELECT_FILE }')); ?>:</label></dt>
		<dd><select id="file" name="file" size="10"><?php $_files_count = (isset($this->_tpldata['files'])) ? sizeof($this->_tpldata['files']) : 0;if ($_files_count) {for ($_files_i = 0; $_files_i < $_files_count; ++$_files_i){$_files_val = &$this->_tpldata['files'][$_files_i]; ?><option value="<?php echo $_files_val['FILE']; ?>"<?php if ($_files_val['S_LAST_ROW']) {  ?> selected="selected"<?php } ?>><?php echo $_files_val['NAME']; ?></option><?php }} ?></select></dd>
	</dl>

	<p class="submit-buttons">
		<input class="button1" type="submit" id="submit" name="submit" value="<?php echo ((isset($this->_rootref['L_START_RESTORE'])) ? $this->_rootref['L_START_RESTORE'] : ((isset($user->lang['START_RESTORE'])) ? $user->lang['START_RESTORE'] : '{ START_RESTORE }')); ?>" />&nbsp;
		<input class="button2" type="submit" id="delete" name="delete" value="<?php echo ((isset($this->_rootref['L_DELETE_BACKUP'])) ? $this->_rootref['L_DELETE_BACKUP'] : ((isset($user->lang['DELETE_BACKUP'])) ? $user->lang['DELETE_BACKUP'] : '{ DELETE_BACKUP }')); ?>" />&nbsp;
		<input class="button2" type="submit" id="download" name="download" value="<?php echo ((isset($this->_rootref['L_DOWNLOAD_BACKUP'])) ? $this->_rootref['L_DOWNLOAD_BACKUP'] : ((isset($user->lang['DOWNLOAD_BACKUP'])) ? $user->lang['DOWNLOAD_BACKUP'] : '{ DOWNLOAD_BACKUP }')); ?>" />
	</p>
	<?php echo (isset($this->_rootref['S_FORM_TOKEN'])) ? $this->_rootref['S_FORM_TOKEN'] : ''; ?>

	</fieldset>
	</form>
	<?php } else { ?>

		<div class="errorbox">
			<p><?php echo ((isset($this->_rootref['L_ACP_NO_ITEMS'])) ? $this->_rootref['L_ACP_NO_ITEMS'] : ((isset($user->lang['ACP_NO_ITEMS'])) ? $user->lang['ACP_NO_ITEMS'] : '{ ACP_NO_ITEMS }')); ?></p>
		</div>
	<?php } } else { ?>

	<h1><?php echo ((isset($this->_rootref['L_ACP_BACKUP'])) ? $this->_rootref['L_ACP_BACKUP'] : ((isset($user->lang['ACP_BACKUP'])) ? $user->lang['ACP_BACKUP'] : '{ ACP_BACKUP }')); ?></h1>

	<p><?php echo ((isset($this->_rootref['L_ACP_BACKUP_EXPLAIN'])) ? $this->_rootref['L_ACP_BACKUP_EXPLAIN'] : ((isset($user->lang['ACP_BACKUP_EXPLAIN'])) ? $user->lang['ACP_BACKUP_EXPLAIN'] : '{ ACP_BACKUP_EXPLAIN }')); ?></p>

	<script type="text/javascript">
	// <![CDATA[

		function selector(bool)
		{
			var table = document.getElementById('table');

			for (var i = 0; i < table.options.length; i++)
			{
				table.options[i].selected = bool;
			}
		}

	// ]]>
	</script>

	<form id="acp_backup" method="post" action="<?php echo (isset($this->_rootref['U_ACTION'])) ? $this->_rootref['U_ACTION'] : ''; ?>">

	<fieldset>
		<legend><?php echo ((isset($this->_rootref['L_BACKUP_OPTIONS'])) ? $this->_rootref['L_BACKUP_OPTIONS'] : ((isset($user->lang['BACKUP_OPTIONS'])) ? $user->lang['BACKUP_OPTIONS'] : '{ BACKUP_OPTIONS }')); ?></legend>
	<dl>
		<dt><label for="type"><?php echo ((isset($this->_rootref['L_BACKUP_TYPE'])) ? $this->_rootref['L_BACKUP_TYPE'] : ((isset($user->lang['BACKUP_TYPE'])) ? $user->lang['BACKUP_TYPE'] : '{ BACKUP_TYPE }')); ?>:</label></dt>
		<dd><label><input type="radio" class="radio" name="type" value="full" id="type" checked="checked" /> <?php echo ((isset($this->_rootref['L_FULL_BACKUP'])) ? $this->_rootref['L_FULL_BACKUP'] : ((isset($user->lang['FULL_BACKUP'])) ? $user->lang['FULL_BACKUP'] : '{ FULL_BACKUP }')); ?></label>
			<label><input type="radio" name="type" class="radio" value="structure" /> <?php echo ((isset($this->_rootref['L_STRUCTURE_ONLY'])) ? $this->_rootref['L_STRUCTURE_ONLY'] : ((isset($user->lang['STRUCTURE_ONLY'])) ? $user->lang['STRUCTURE_ONLY'] : '{ STRUCTURE_ONLY }')); ?></label>
			<label><input type="radio" class="radio" name="type" value="data" /> <?php echo ((isset($this->_rootref['L_DATA_ONLY'])) ? $this->_rootref['L_DATA_ONLY'] : ((isset($user->lang['DATA_ONLY'])) ? $user->lang['DATA_ONLY'] : '{ DATA_ONLY }')); ?></label></dd>
	</dl>
	<dl>
		<dt><label for="method"><?php echo ((isset($this->_rootref['L_FILE_TYPE'])) ? $this->_rootref['L_FILE_TYPE'] : ((isset($user->lang['FILE_TYPE'])) ? $user->lang['FILE_TYPE'] : '{ FILE_TYPE }')); ?>:</label></dt>
		<dd><?php $_methods_count = (isset($this->_tpldata['methods'])) ? sizeof($this->_tpldata['methods']) : 0;if ($_methods_count) {for ($_methods_i = 0; $_methods_i < $_methods_count; ++$_methods_i){$_methods_val = &$this->_tpldata['methods'][$_methods_i]; ?>

		<label><input name="method"<?php if ($_methods_val['S_FIRST_ROW']) {  ?> id="method" checked="checked"<?php } ?> type="radio" class="radio" value="<?php echo $_methods_val['TYPE']; ?>" /> <?php echo $_methods_val['TYPE']; ?></label>
		<?php }} ?></dd>
	</dl>
	<dl>
		<dt><label for="where"><?php echo ((isset($this->_rootref['L_ACTION'])) ? $this->_rootref['L_ACTION'] : ((isset($user->lang['ACTION'])) ? $user->lang['ACTION'] : '{ ACTION }')); ?>:</label></dt>
		<dd>
			<label><input id="where" type="radio" class="radio" name="where" value="store" checked="checked" /> <?php echo ((isset($this->_rootref['L_STORE_LOCAL'])) ? $this->_rootref['L_STORE_LOCAL'] : ((isset($user->lang['STORE_LOCAL'])) ? $user->lang['STORE_LOCAL'] : '{ STORE_LOCAL }')); ?></label>
			<label><input type="radio" class="radio" name="where" value="download" /> <?php echo ((isset($this->_rootref['L_DOWNLOAD'])) ? $this->_rootref['L_DOWNLOAD'] : ((isset($user->lang['DOWNLOAD'])) ? $user->lang['DOWNLOAD'] : '{ DOWNLOAD }')); ?></label>
		</dd>
	</dl>
	<dl>
		<dt><label for="table"><?php echo ((isset($this->_rootref['L_TABLE_SELECT'])) ? $this->_rootref['L_TABLE_SELECT'] : ((isset($user->lang['TABLE_SELECT'])) ? $user->lang['TABLE_SELECT'] : '{ TABLE_SELECT }')); ?>:</label></dt>
		<dd><select id="table" name="table[]" size="10" multiple="multiple">
		<?php $_tables_count = (isset($this->_tpldata['tables'])) ? sizeof($this->_tpldata['tables']) : 0;if ($_tables_count) {for ($_tables_i = 0; $_tables_i < $_tables_count; ++$_tables_i){$_tables_val = &$this->_tpldata['tables'][$_tables_i]; ?>

			<option value="<?php echo $_tables_val['TABLE']; ?>"><?php echo $_tables_val['TABLE']; ?></option>
		<?php }} ?>

		</select></dd>
		<dd><a href="#" onclick="selector(true); return false;"><?php echo ((isset($this->_rootref['L_SELECT_ALL'])) ? $this->_rootref['L_SELECT_ALL'] : ((isset($user->lang['SELECT_ALL'])) ? $user->lang['SELECT_ALL'] : '{ SELECT_ALL }')); ?></a> :: <a href="#" onclick="selector(false); return false;"><?php echo ((isset($this->_rootref['L_DESELECT_ALL'])) ? $this->_rootref['L_DESELECT_ALL'] : ((isset($user->lang['DESELECT_ALL'])) ? $user->lang['DESELECT_ALL'] : '{ DESELECT_ALL }')); ?></a></dd>
	</dl>

	<p class="submit-buttons">
		<input class="button1" type="submit" id="submit" name="submit" value="<?php echo ((isset($this->_rootref['L_SUBMIT'])) ? $this->_rootref['L_SUBMIT'] : ((isset($user->lang['SUBMIT'])) ? $user->lang['SUBMIT'] : '{ SUBMIT }')); ?>" />&nbsp;
		<input class="button2" type="reset" id="reset" name="reset" value="<?php echo ((isset($this->_rootref['L_RESET'])) ? $this->_rootref['L_RESET'] : ((isset($user->lang['RESET'])) ? $user->lang['RESET'] : '{ RESET }')); ?>" />
	</p>
	<?php echo (isset($this->_rootref['S_FORM_TOKEN'])) ? $this->_rootref['S_FORM_TOKEN'] : ''; ?>

	</fieldset>
	</form>

<?php } $this->_tpl_include('overall_footer.html'); ?>