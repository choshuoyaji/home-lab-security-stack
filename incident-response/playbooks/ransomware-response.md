# 🚨 Ransomware Incident Response Playbook

> Home Lab IR Playbook — Takahiro Oda

## Phase 1: Detection & Identification

### Indicators
- [ ] Mass file encryption (extension changes: `.encrypted`, `.locked`, `.crypted`)
- [ ] Ransom note files (`README.txt`, `DECRYPT_FILES.html`)
- [ ] Unusual CPU/disk usage spikes
- [ ] Shadow copy deletion attempts (`vssadmin delete shadows`)
- [ ] Wazuh alerts: Rule IDs 87400-87499

### Sigma Rules (from this repo)
```yaml
# See: detection-engineering/sigma-rules/
- proc_creation_win_ransomware_indicators.yml
- file_event_win_mass_encryption.yml
- proc_creation_win_shadow_copy_deletion.yml
```

## Phase 2: Containment

### Immediate Actions (< 15 minutes)
1. **Network Isolation**
   ```bash
   # Isolate affected host via CrowdStrike
   falconctl -s --cid=<CID> --aid=<AID> --contain
   
   # Or via network firewall
   iptables -A INPUT -s <infected_ip> -j DROP
   iptables -A OUTPUT -d <infected_ip> -j DROP
   ```

2. **Disable Compromised Accounts**
   ```powershell
   Disable-ADAccount -Identity <username>
   ```

3. **Preserve Evidence**
   ```bash
   # Memory dump
   sudo avml /evidence/$(hostname)_$(date +%Y%m%d_%H%M%S).lime
   
   # Disk image (if feasible)
   sudo dc3dd if=/dev/sda of=/evidence/disk.dd hash=sha256 log=/evidence/hash.log
   ```

## Phase 3: Eradication

### Analysis
- [ ] Identify ransomware variant (check [ID Ransomware](https://id-ransomware.malwarehunterteam.com/))
- [ ] Determine initial access vector
- [ ] Map lateral movement path
- [ ] Identify all affected systems

### Cleanup
- [ ] Remove persistence mechanisms
- [ ] Patch exploited vulnerabilities
- [ ] Reset all compromised credentials
- [ ] Update detection rules based on findings

## Phase 4: Recovery

### Restore Priority
1. Domain Controllers
2. Critical business applications
3. File servers
4. User workstations

### Restoration Steps
- [ ] Verify clean backups exist
- [ ] Restore from known-good backup
- [ ] Validate system integrity
- [ ] Monitor for reinfection (48-hour watch)

## Phase 5: Lessons Learned

### Post-Incident Review (within 5 business days)
- [ ] Timeline reconstruction
- [ ] Root cause analysis
- [ ] Detection gap analysis
- [ ] Update this playbook
- [ ] Update Sigma rules in `detection-engineering/`
- [ ] Brief stakeholders

## SOAR Automation
See `soar/playbooks/ransomware-auto-contain.yml` for automated containment workflow.
