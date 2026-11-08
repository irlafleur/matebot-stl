// MateBot - Arduino Yun + Waveshare Bus Servo Adapter (A) - 6 x STS3215 en serie
// Protocole Feetech STS : FF FF ID LEN INSTR PARAMS CHK
// Serial  = USB (moniteur serie, 115200)
// Serial1 = broches 0 (RX) / 1 (TX) -> adaptateur Waveshare (cavalier en A)
// IMPORTANT : ne PAS utiliser Bridge.h dans ce sketch.

const uint8_t  NB = 6;
uint8_t  IDS[NB] = {1, 2, 3, 4, 5, 6};
const long BUS_BAUD = 1000000;   // defaut STS3215

void writePacket(uint8_t id, uint8_t instr, const uint8_t *p, uint8_t n) {
  uint8_t len = n + 2, chk = id + len + instr;
  Serial1.write(0xFF); Serial1.write(0xFF);
  Serial1.write(id); Serial1.write(len); Serial1.write(instr);
  for (uint8_t i = 0; i < n; i++) { Serial1.write(p[i]); chk += p[i]; }
  Serial1.write((uint8_t)~chk);
  Serial1.flush();
}

void clearRx() { while (Serial1.available()) Serial1.read(); }

// Lit une reponse ; retourne nb d'octets de parametres ou -1
int readReply(uint8_t id, uint8_t *out, uint8_t maxN, unsigned long tmo = 20) {
  unsigned long t = millis(); uint8_t buf[16]; uint8_t k = 0;
  while (millis() - t < tmo && k < sizeof(buf)) {
    if (Serial1.available()) buf[k++] = Serial1.read();
    // l'adaptateur renvoie l'echo de notre trame : on cherche FF FF id
    for (uint8_t s = 0; s + 5 < k; s++) {
      if (buf[s] == 0xFF && buf[s+1] == 0xFF && buf[s+2] == id) {
        uint8_t len = buf[s+3];
        if (k >= s + 4 + len) {
          if (buf[s+4] > 0x0F) continue;  // pas un octet d'erreur -> echo
          uint8_t n = len - 2; if (n > maxN) n = maxN;
          for (uint8_t i = 0; i < n; i++) out[i] = buf[s+5+i];
          return n;
        }
      }
    }
  }
  return -1;
}

bool ping(uint8_t id) {
  clearRx(); writePacket(id, 0x01, nullptr, 0);
  uint8_t d[2]; return readReply(id, d, 2) >= 0;
}

// position 0..4095 (2048 = centre), vitesse en pas/s (0 = max), acc 0..254
void moveTo(uint8_t id, int pos, int speed = 1500, uint8_t acc = 50) {
  uint8_t p[8] = {0x29, acc, (uint8_t)(pos & 0xFF), (uint8_t)(pos >> 8),
                  0, 0, (uint8_t)(speed & 0xFF), (uint8_t)(speed >> 8)};
  writePacket(id, 0x03, p, 8);
}

int readPos(uint8_t id) {
  clearRx(); uint8_t p[2] = {0x38, 2}; writePacket(id, 0x02, p, 2);
  uint8_t d[2]; if (readReply(id, d, 2) != 2) return -1;
  return d[0] | (d[1] << 8);
}

void torque(uint8_t id, bool on) { uint8_t p[2] = {0x28, on}; writePacket(id, 0x03, p, 2); }

void scan() {
  for (uint8_t i = 0; i < NB; i++) {
    Serial.print("ID "); Serial.print(IDS[i]);
    if (ping(IDS[i])) { Serial.print(" OK  pos="); Serial.println(readPos(IDS[i])); }
    else Serial.println(" -- pas de reponse");
  }
}

void sweep() {
  for (uint8_t i = 0; i < NB; i++) moveTo(IDS[i], 1500);
  delay(1500);
  for (uint8_t i = 0; i < NB; i++) moveTo(IDS[i], 2600);
  delay(1500);
  for (uint8_t i = 0; i < NB; i++) moveTo(IDS[i], 2048);
}

void setup() {
  Serial.begin(115200);
  Serial1.begin(BUS_BAUD);
  while (!Serial && millis() < 5000) {}
  Serial.println(F("MateBot - 6 servos STS3215"));
  Serial.println(F("Commandes : scan | sweep | m <id> <pos> | r <id> | off | on"));
  scan();
}

void loop() {
  if (!Serial.available()) return;
  String c = Serial.readStringUntil('\n'); c.trim();
  if (c == "scan") scan();
  else if (c == "sweep") sweep();
  else if (c == "off") { for (uint8_t i = 0; i < NB; i++) torque(IDS[i], false); Serial.println("couple coupe"); }
  else if (c == "on")  { for (uint8_t i = 0; i < NB; i++) torque(IDS[i], true);  Serial.println("couple actif"); }
  else if (c.startsWith("m ")) {
    int id, pos; if (sscanf(c.c_str(), "m %d %d", &id, &pos) == 2) {
      pos = constrain(pos, 0, 4095); moveTo(id, pos); Serial.print("ID "); Serial.print(id); Serial.print(" -> "); Serial.println(pos);
    }
  }
  else if (c.startsWith("r ")) { int id = c.substring(2).toInt(); Serial.print("pos="); Serial.println(readPos(id)); }
  else Serial.println("commande inconnue");
}
