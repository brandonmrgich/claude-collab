# Calm Collective: Venue Photos

The real assets. These ten photos are lazy-loaded from a CDN
in the main page's gallery, which is why the first-pass scrape
missed them — `wget` only follows rendered `src` attributes,
not `data-src` behind a JavaScript loader.

Fetched them by hand into
`~/showell_repos/calm-collective/venue-photos/{1..10}.jpg`.

These are the only genuinely-venue-specific images we have.
Everything in the prior catalog was template filler. Anything
sane we do with these photos — gallery, hero, Instagram-style
grid — is already an upgrade.

One quick note on the set: **#2 and #8 are the same photo.**
Someone uploaded it twice. That's worth flagging; it's the
kind of detail a tidy reskin fixes silently.

## 1. Exterior, night

![1.jpg](/scrape/venue-photos/1.jpg)

Storefront at dusk. Illuminated white channel letters reading
"KAVA BAR," with the Calm Collective Lounge logo (a stylized
tree inside a circle, with "CALM COLLECTIVE" and "LOUNGE"
around the ring) to the left of the text. Address "160" on
the door, pink neon glow visible inside. Deep blue sky.

This is the closest thing to a brand hero image. The logo
here is sharp and readable — worth lifting out as its own
asset.

## 2. Pink cocktail + chess set

![2.jpg](/scrape/venue-photos/2.jpg)

Foreground: a coral/pink cocktail in a ribbed glass on a
patterned coaster, garnished with a lemon wheel and two
maraschino cherries. Behind it on the same wooden table: an
open wooden chess set mid-game. Further back: a leather lounge
chair, then a pool table with someone in a dark shirt setting
it up, and a grass-wall backdrop.

This is the most "character of the place" single image in
the set. Drink + chess + pool + lounge chair tells the venue
story in one frame.

## 3. Bar counter, people working

![3.jpg](/scrape/venue-photos/3.jpg)

Wide shot from behind the bar looking out. Barista/staff
behind the counter, a male customer in a blue shirt typing on
a laptop at the bar with a glass of iced coffee, another
customer in the mid-ground, a "Kava Vapes" countertop display
with a pink orchid in a vase, multiple TVs on the walls showing
what looks like sports or content loops, a neon "Calm Coll…"
sign on the far wall (partially obscured), pool table visible
through to the back. Phone case/accessory rack at far left.

The "third space / coworking / hang out" story, visually. This
is the photo that says "come work from here."

## 4. Pool table in use

![4.jpg](/scrape/venue-photos/4.jpg)

Interior pool shot. A man in a patterned white shirt leaning
on the cushion to take a shot with a cue. Green felt table,
balls mid-rack. Karaoke screen mounted above (you can see
"Flowers / Miley Cyrus" listed among queued songs). Artificial
grass wall behind the table.

The karaoke detail is useful — sells a feature that would
otherwise need a separate photo.

## 5. Menu + two signature drinks

![5.jpg](/scrape/venue-photos/5.jpg)

A menu card propped on a round wooden table, flanked by two
branded cups (one pink, one yellow) on decorative coasters.
Above the menu, the large circular Calm Collective Lounge
logo is mounted on the grass wall, glowing. Menu headings
visible: TRADITIONAL KAVA, BOTANICAL TEAS, SNACKS AND SODAS,
MOCKTAILS.

This is *the* menu shot. Legible enough to be informative.
Good candidate for the actual /menu page.

## 6. Blue cocktail, neon background

![6.jpg](/scrape/venue-photos/6.jpg)

A tall blue cocktail (blue curaçao-style color) with a lemon
wheel on the rim, on a reflective dark metal tabletop. Blurred
background: yellow neon sign, pool table, grass wall.

Moody product shot. The composition is strong; the color pops
against the green/black background.

## 7. White Rabbit cans

![7.jpg](/scrape/venue-photos/7.jpg)

Two tall slim cans side by side on a reflective black bartop,
labeled "WHITE RABBIT." Both marked "ZERO SUGAR ★ ZERO
ALCOHOL." Left can: "Root Beer Kratom Seltzer," energy
variant. Right can: "Lemon Iced Tea," social variant.

Brand-partner product shot. Probably useful if the site has a
"what we serve" or retail section; less so for hero imagery.

## 8. (duplicate of #2)

![8.jpg](/scrape/venue-photos/8.jpg)

Identical to photo #2 as far as I can tell — same pink
cocktail, same chess set, same background setup. I'd flag this
and pick one for any new gallery.

## 9. Kombucha + syrup taps

![9.jpg](/scrape/venue-photos/9.jpg)

Close-up of the tap tower: four chrome taps, two with wooden
handle plates reading "LIQUID SUNSHINE" and "BOTANICAL BEER"
(with a "21+ ONLY" red sticker on the latter). A promotional
card explains "We are a craft kombucha brewery from Merritt
Island FL… Big Dog Kombucha." Behind the taps: a row of
Monin flavored-syrup pump bottles.

Good "real beverage program" photo. The 21+ sticker is
interesting — it means part of the kava bar's offering is
age-restricted, which is a detail a reskin should either
highlight or carefully background.

## 10. Pouring a drink

![10.jpg](/scrape/venue-photos/10.jpg)

Close-up of a hand with polished nails pouring frothed white
cream (probably coconut milk or a kava-traditional topping?)
from a small metal pitcher into a small dark porcelain cup on
a matching saucer. The cup contains a darker liquid already.
Dark, moody lighting.

Reads as "kava preparation ritual" — close-up, artisanal.
Best candidate for a "how we make it" or "our process"
section.

---

## Quick summary

Ten photos, one duplicate (#2 = #8), so effectively **nine
unique assets**.

What they give us, rolling it up:

- **One strong exterior / brand shot** (#1).
- **One atmosphere anchor** (#2/#8 — drink + chess + pool in
  one frame).
- **One coworking / third-space shot** (#3).
- **Two feature-specific shots**: pool + karaoke (#4), menu
  readout (#5).
- **Two product shots of signature drinks** (#6 blue cocktail,
  #10 pouring ritual).
- **Two partner-product shots** (#7 White Rabbit cans, #9 Big
  Dog Kombucha taps).

Everything in the template image set (the prior catalog)
directly misrepresents what the place actually is. Everything
in this set tells a version of the real story. The reskin
should lead with these.
