<?php
require dirname(__DIR__) . '/app/bootstrap.php';

$status = samp_status();
$registered = stat_registered();
$ip = cfg('server.host') . ':' . (int)cfg('server.port');

$pageTitle = 'Portal';
$active = 'home';
$bodyClass = 'page-home';
require APP_DIR . '/views/header.php';
?>

<section class="hero">
  <div class="hero-bg" style="background-image:url('<?= asset('img/gallery/events.jpg') ?>')"></div>
  <div class="wrap hero-in">
    <div class="hero-copy">
      <span class="eyebrow"><span class="dot <?= $status['online'] ? 'live' : '' ?>"></span> SA-MP RolePlay · Balkan</span>
      <h1><span class="h-black">BLACK</span><span class="h-jack">JACK</span><em>RolePlay</em></h1>
      <p class="lead">Najveća balkanska RolePlay zajednica. Organizacije, poslovi, policija, eventi i ekonomija koju grade igrači — sve na jednom mestu.</p>

      <div class="ip-box">
        <div class="ip-label">IP adresa servera</div>
        <div class="ip-row">
          <code id="server-ip"><?= e($ip) ?></code>
          <button class="ip-copy" data-copy="<?= e($ip) ?>" aria-label="Kopiraj IP"><?= icon('copy') ?><span>Kopiraj</span></button>
        </div>
      </div>

      <div class="hero-cta">
        <a class="btn btn-lg" href="samp://<?= e($ip) ?>"><?= icon('play') ?> Uđi u igru</a>
        <?php if (is_logged_in()): ?>
          <a class="btn btn-lg btn-ghost" href="<?= url('ucp/') ?>"><?= icon('user') ?> Moj UCP</a>
        <?php else: ?>
          <a class="btn btn-lg btn-ghost" href="<?= url('register.php') ?>"><?= icon('id') ?> Napravi nalog</a>
        <?php endif; ?>
      </div>
    </div>

    <div class="hero-art">
      <div class="chip-ring"></div>
      <img class="hero-logo" src="<?= asset('img/logo.png') ?>" alt="Black Jack RolePlay" width="507" height="668">
      <div class="float-card fc-1"><b>A</b><i>♠</i></div>
      <div class="float-card fc-2"><b>J</b><i>♣</i></div>
    </div>
  </div>

  <div class="wrap">
    <div class="stat-strip" id="server">
      <div class="stat">
        <span class="stat-k"><?= icon('user') ?> Online</span>
        <span class="stat-v"><b id="st-players"><?= $status['online'] ? (int)$status['players'] : '—' ?></b><small id="st-max"><?= $status['online'] ? '/ ' . (int)$status['max'] : '' ?></small></span>
        <span class="stat-s" id="st-state"><?= $status['online'] ? 'Server je online' : 'Server je offline' ?></span>
      </div>
      <div class="stat">
        <span class="stat-k"><?= icon('star') ?> Rekord</span>
        <span class="stat-v"><b><?= (int)cfg('server.record') ?></b></span>
        <span class="stat-s">igrača istovremeno</span>
      </div>
      <div class="stat">
        <span class="stat-k"><?= icon('id') ?> Registrovano</span>
        <span class="stat-v"><b><?= $registered !== null ? number_format($registered, 0, ',', '.') : '—' ?></b></span>
        <span class="stat-s">naloga u bazi</span>
      </div>
      <div class="stat">
        <span class="stat-k"><?= icon('clock') ?> Happy Hours</span>
        <span class="stat-v"><b>X3</b></span>
        <span class="stat-s">XP do levela 10</span>
      </div>
    </div>
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <div class="sec-head">
      <span class="kicker">♠ Šta te čeka</span>
      <h2>Grad koji živi 24/7</h2>
      <p>Od prvog posla na stovarištu do vrha mafijaške porodice — ti biraš svoj put.</p>
    </div>
    <div class="features">
      <article class="feat">
        <div class="feat-ico"><?= icon('shield') ?></div>
        <h3>Legalne organizacije</h3>
        <p>Chicago Police Department, bolnica, vlada — patrole, hapšenja, akcije i sopstvena hijerarhija.</p>
      </article>
      <article class="feat">
        <div class="feat-ico"><?= icon('gun') ?></div>
        <h3>Ilegalne organizacije</h3>
        <p>Bande, mafije i karteli. Teritorije, šverc i rat za kraj — samo najjači ostaju na vrhu.</p>
      </article>
      <article class="feat">
        <div class="feat-ico"><?= icon('job') ?></div>
        <h3>Poslovi &amp; ekonomija</h3>
        <p>Mesar, stočar, kamiondžija i još mnogo toga. Happy Job svakog dana nosi duplu platu.</p>
      </article>
      <article class="feat">
        <div class="feat-ico"><?= icon('car') ?></div>
        <h3>Vozila &amp; imovina</h3>
        <p>Kupi kuću, firmu ili vozilo iz snova. Banka, zlato i tržište koje kreiraju igrači.</p>
      </article>
      <article class="feat">
        <div class="feat-ico"><?= icon('cal') ?></div>
        <h3>Eventi</h3>
        <p>Redovni eventi sa stotinama igrača, nagrade za organizacije i specijalni Happy Hours.</p>
      </article>
      <article class="feat">
        <div class="feat-ico"><?= icon('vip') ?></div>
        <h3>VIP &amp; Promoteri</h3>
        <p>Bronze, Silver, Gold, Platinum i Diamond paketi. Podrži server i izdvoji se u gradu.</p>
      </article>
    </div>
  </div>
</section>

<section class="sec sec-hc" id="high-command">
  <div class="wrap">
    <div class="sec-head">
      <span class="kicker">♣ Uprava servera</span>
      <h2>High Command</h2>
      <p>Ljudi koji stoje iza Black Jack-a. Za sve ozbiljne stvari — obrati se upravi na Discordu.</p>
    </div>
    <div class="hc-grid">
      <?php foreach (cfg('staff', []) as $s): $red = in_array($s['suit'], ['♥', '♦'], true); ?>
      <article class="hc-card <?= $red ? 'red' : '' ?>" tabindex="0">
        <div class="hc-corner tl"><b><?= e($s['card']) ?></b><i><?= e($s['suit']) ?></i></div>
        <div class="hc-corner br"><b><?= e($s['card']) ?></b><i><?= e($s['suit']) ?></i></div>
        <div class="hc-stage">
          <div class="hc-chip"></div>
          <img src="<?= e(skin_url((int)$s['skin'])) ?>" alt="<?= e($s['name']) ?> skin" loading="lazy" width="165" height="300">
        </div>
        <div class="hc-info">
          <span class="hc-role"><?= e($s['role']) ?></span>
          <h3><?= e($s['name']) ?></h3>
          <span class="hc-skin">Skin ID <?= (int)$s['skin'] ?></span>
        </div>
      </article>
      <?php endforeach; ?>
    </div>
  </div>
</section>

<section class="sec" id="galerija">
  <div class="wrap">
    <div class="sec-head">
      <span class="kicker">♦ Sa servera</span>
      <h2>Galerija</h2>
      <p>Trenuci iz grada — eventi, akcije i organizacije.</p>
    </div>
    <div class="gallery">
      <?php
      $gal = [
          ['events.jpg', 'Event sa 490+ igrača'],
          ['policija.jpg', 'Chicago Police Department'],
          ['akcija.jpg', 'Akcija ispred policijske stanice'],
          ['grove.jpg', 'Grove Street'],
      ];
      foreach ($gal as $i => [$img, $cap]): ?>
      <figure class="g-item <?= $i === 0 ? 'g-big' : ($i === 1 ? 'g-wide' : '') ?>">
        <a href="<?= asset('img/gallery/' . $img) ?>" class="lb" data-cap="<?= e($cap) ?>">
          <img src="<?= asset('img/gallery/' . $img) ?>" alt="<?= e($cap) ?>" loading="lazy">
        </a>
        <figcaption><?= e($cap) ?></figcaption>
      </figure>
      <?php endforeach; ?>
    </div>
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <div class="cta">
      <div>
        <h2>Spreman za prvu ruku?</h2>
        <p>Napravi nalog za 30 sekundi, uđi u igru i prati svoj napredak u User Control Panelu.</p>
      </div>
      <div class="cta-btns">
        <a class="btn btn-lg" href="<?= url(is_logged_in() ? 'ucp/' : 'register.php') ?>"><?= is_logged_in() ? 'Otvori UCP' : 'Registruj se' ?></a>
        <a class="btn btn-lg btn-ghost" href="<?= e(cfg('site.discord')) ?>" target="_blank" rel="noopener"><?= icon('chat') ?> Discord</a>
      </div>
    </div>
  </div>
</section>

<div class="lightbox" hidden><button class="lb-close" aria-label="Zatvori">×</button><img alt=""><p></p></div>
<script>window.BJ_STATUS_URL = <?= json_encode(url('api/status.php')) ?>;</script>

<?php require APP_DIR . '/views/footer.php'; ?>
