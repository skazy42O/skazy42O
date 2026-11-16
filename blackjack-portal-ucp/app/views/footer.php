<footer class="foot">
  <div class="wrap foot-in">
    <div class="foot-brand">
      <img src="<?= asset('img/logo-sm.png') ?>" alt="" width="46" height="61">
      <div>
        <b>BLACK JACK RolePlay</b>
        <span><?= e(cfg('site.tagline')) ?></span>
      </div>
    </div>
    <div class="foot-links">
      <a href="<?= url('') ?>">Portal</a>
      <a href="<?= url('ucp/') ?>">UCP</a>
      <a href="<?= e(cfg('site.discord')) ?>" target="_blank" rel="noopener">Discord</a>
      <a href="samp://<?= e(cfg('server.host')) ?>:<?= (int)cfg('server.port') ?>">Poveži se</a>
    </div>
    <div class="foot-copy">
      <span class="suits">♠ ♥ ♦ ♣</span>
      © <?= date('Y') ?> <?= e(cfg('site.website')) ?> · Nismo povezani sa Rockstar Games / Take-Two.
    </div>
  </div>
</footer>
<script src="<?= asset('js/main.js') ?>" defer></script>
</body>
</html>
