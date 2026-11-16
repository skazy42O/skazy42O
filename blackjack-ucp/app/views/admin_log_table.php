<?php /** @var array $logRows */ ?>
<div class="table-wrap">
  <table class="tbl">
    <thead><tr><th>Vreme</th><th>Admin</th><th>Akcija</th><th>Meta</th><th>Detalji</th></tr></thead>
    <tbody>
    <?php if (!$logRows): ?><tr><td colspan="5" class="empty">Još nema zabeleženih akcija.</td></tr><?php endif; ?>
    <?php foreach ($logRows as $l): ?>
      <tr>
        <td data-l="Vreme" class="nowrap"><?= e(date('d.m.Y H:i', strtotime($l['created_at']))) ?></td>
        <td data-l="Admin"><b><?= e($l['admin_name']) ?></b></td>
        <td data-l="Akcija"><span class="pill pill-<?= e(['ban' => 'red', 'unban' => 'green', 'edit' => 'blue', 'admin' => 'gold', 'login' => 'muted'][$l['action']] ?? 'muted') ?>"><?= e($l['action']) ?></span></td>
        <td data-l="Meta"><?= e($l['target'] ?? '—') ?></td>
        <td data-l="Detalji" class="wrap-any"><?= e($l['details']) ?></td>
      </tr>
    <?php endforeach; ?>
    </tbody>
  </table>
</div>
