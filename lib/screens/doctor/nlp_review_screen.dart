// lib/screens/doctor/nlp_review_screen.dart
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../../theme/app_theme.dart';
import '../../models/blood_cancer_ehr_model.dart';
import '../../models/nlp_extraction_model.dart';
import '../../services/doctor_service.dart';

class NlpReviewScreen extends StatefulWidget {
  final String patientId;
  final String patientName;
  final String doctorId;
  final String doctorName;
  final BloodCancerEhrModel? currentEhr;
  final NlpExtractionResponse extraction;

  const NlpReviewScreen({
    super.key,
    required this.patientId,
    required this.patientName,
    required this.doctorId,
    required this.doctorName,
    this.currentEhr,
    required this.extraction,
  });

  @override
  State<NlpReviewScreen> createState() => _NlpReviewScreenState();
}

class _NlpReviewScreenState extends State<NlpReviewScreen> {
  final _service = DoctorService();
  bool _saving = false;

  // Editable Symptoms: map of symptomKey -> bool? (true: present, false: negated, null: unstated)
  late Map<String, bool?> _symptomsState;
  late Map<String, String?> _symptomsTrace;

  // Editable CBC Controllers
  late TextEditingController _wbcCtrl;
  late TextEditingController _rbcCtrl;
  late TextEditingController _hbCtrl;
  late TextEditingController _hctCtrl;
  late TextEditingController _pltCtrl;
  late TextEditingController _neutroAbsCtrl;
  late TextEditingController _neutroPctCtrl;
  late TextEditingController _lymphoAbsCtrl;
  late TextEditingController _lymphoPctCtrl;
  late TextEditingController _monoAbsCtrl;
  late TextEditingController _monoPctCtrl;
  late TextEditingController _eosAbsCtrl;
  late TextEditingController _eosPctCtrl;
  late TextEditingController _basoAbsCtrl;
  late TextEditingController _basoPctCtrl;
  late TextEditingController _rdwSdCtrl;
  late TextEditingController _rdwCvCtrl;

  // Editable Other Controllers
  late TextEditingController _diseaseTypeCtrl;
  late TextEditingController _subtypeCtrl;
  late TextEditingController _stageCtrl;
  late TextEditingController _statusCtrl;
  late TextEditingController _blastPctCtrl;
  late TextEditingController _boneMarrowCtrl;
  late TextEditingController _chemoCtrl;
  late TextEditingController _notesCtrl;

  final Map<String, String> _symptomLabels = {
    'shortnessOfBreath': 'Shortness of Breath',
    'bonePain': 'Bone / Joint Pain',
    'fever': 'Persistent Fever',
    'familyHistory': 'Family History of Hematologic Disorders',
    'frequentInfections': 'Frequent / Recurrent Infections',
    'itchySkinOrRash': 'Itchy Skin / Cutaneous Rash',
    'lossOfAppetiteOrNausea': 'Loss of Appetite / Nausea',
    'persistentWeaknessAndFatigue': 'Persistent Weakness & Fatigue',
    'swollenPainlessLymphNodes': 'Swollen Painless Lymph Nodes',
    'significantBruisingOrBleeding': 'Significant Bruising / Bleeding',
    'enlargedLiver': 'Enlarged Liver / Spleen',
    'oralCavityChanges': 'Oral Cavity Changes / Mouth Sores',
    'visionBlurring': 'Vision Blurring / Visual Disturbances',
    'jaundice': 'Jaundice / Scleral Icterus',
    'nightSweats': 'Drenching Night Sweats',
    'smokes': 'History of Smoking / Tobacco Use',
  };

  @override
  void initState() {
    super.initState();
    _initValues();
  }

  void _initValues() {
    _symptomsState = {};
    _symptomsTrace = {};

    // Initialize 16 symptoms from existing EHR or extracted results
    _symptomLabels.forEach((k, _) {
      if (widget.extraction.symptoms.containsKey(k)) {
        final item = widget.extraction.symptoms[k]!;
        _symptomsState[k] = item.value;
        _symptomsTrace[k] = item.sourceText;
      } else if (widget.currentEhr != null) {
        final existingMap = widget.currentEhr!.symptoms.toMap();
        _symptomsState[k] = existingMap[k] as bool?;
        _symptomsTrace[k] = null;
      } else {
        _symptomsState[k] = null;
        _symptomsTrace[k] = null;
      }
    });

    final cbcExt = widget.extraction.cbc;
    final currCbc = widget.currentEhr?.cbc;

    _wbcCtrl = TextEditingController(text: cbcExt.wbc?.value?.toString() ?? currCbc?.wbc?.toString() ?? '');
    _rbcCtrl = TextEditingController(text: cbcExt.rbc?.value?.toString() ?? currCbc?.rbc?.toString() ?? '');
    _hbCtrl = TextEditingController(text: cbcExt.hemoglobin?.value?.toString() ?? currCbc?.hemoglobin?.toString() ?? '');
    _hctCtrl = TextEditingController(text: cbcExt.hematocrit?.value?.toString() ?? currCbc?.hematocrit?.toString() ?? '');
    _pltCtrl = TextEditingController(text: cbcExt.platelets?.value?.toString() ?? currCbc?.platelets?.toString() ?? '');

    _neutroAbsCtrl = TextEditingController(text: cbcExt.neutrophils?.absolute?.toString() ?? currCbc?.neutrophils?.absolute?.toString() ?? '');
    _neutroPctCtrl = TextEditingController(text: cbcExt.neutrophils?.percentage?.toString() ?? currCbc?.neutrophils?.percentage?.toString() ?? '');
    _lymphoAbsCtrl = TextEditingController(text: cbcExt.lymphocytes?.absolute?.toString() ?? currCbc?.lymphocytes?.absolute?.toString() ?? '');
    _lymphoPctCtrl = TextEditingController(text: cbcExt.lymphocytes?.percentage?.toString() ?? currCbc?.lymphocytes?.percentage?.toString() ?? '');
    _monoAbsCtrl = TextEditingController(text: cbcExt.monocytes?.absolute?.toString() ?? currCbc?.monocytes?.absolute?.toString() ?? '');
    _monoPctCtrl = TextEditingController(text: cbcExt.monocytes?.percentage?.toString() ?? currCbc?.monocytes?.percentage?.toString() ?? '');
    _eosAbsCtrl = TextEditingController(text: cbcExt.eosinophils?.absolute?.toString() ?? currCbc?.eosinophils?.absolute?.toString() ?? '');
    _eosPctCtrl = TextEditingController(text: cbcExt.eosinophils?.percentage?.toString() ?? currCbc?.eosinophils?.percentage?.toString() ?? '');
    _basoAbsCtrl = TextEditingController(text: cbcExt.basophils?.absolute?.toString() ?? currCbc?.basophils?.absolute?.toString() ?? '');
    _basoPctCtrl = TextEditingController(text: cbcExt.basophils?.percentage?.toString() ?? currCbc?.basophils?.percentage?.toString() ?? '');
    _rdwSdCtrl = TextEditingController(text: cbcExt.rdwSd?.value?.toString() ?? currCbc?.rdwSd?.toString() ?? '');
    _rdwCvCtrl = TextEditingController(text: cbcExt.rdwCv?.value?.toString() ?? currCbc?.rdwCv?.toString() ?? '');

    final otherExt = widget.extraction.other;
    final currEhr = widget.currentEhr;

    _diseaseTypeCtrl = TextEditingController(text: otherExt.diseaseType ?? currEhr?.diseaseType ?? '');
    _subtypeCtrl = TextEditingController(text: otherExt.diagnosisSubtype ?? currEhr?.diagnosisSubtype ?? '');
    _stageCtrl = TextEditingController(text: otherExt.stage ?? currEhr?.stage ?? '');
    _statusCtrl = TextEditingController(text: otherExt.diagnosisStatus ?? currEhr?.diagnosisStatus ?? '');
    _blastPctCtrl = TextEditingController(text: otherExt.blastCellPercentage?.toString() ?? currEhr?.blastCellPercentage?.toString() ?? '');
    _boneMarrowCtrl = TextEditingController(text: otherExt.boneMarrowBiopsy ?? currEhr?.boneMarrowBiopsy ?? '');
    _chemoCtrl = TextEditingController(text: otherExt.chemotherapy ?? currEhr?.chemotherapy ?? '');
    _notesCtrl = TextEditingController(text: widget.extraction.text.isNotEmpty ? widget.extraction.text : (currEhr?.clinicalNotes ?? ''));
  }

  @override
  void dispose() {
    _wbcCtrl.dispose();
    _rbcCtrl.dispose();
    _hbCtrl.dispose();
    _hctCtrl.dispose();
    _pltCtrl.dispose();
    _neutroAbsCtrl.dispose();
    _neutroPctCtrl.dispose();
    _lymphoAbsCtrl.dispose();
    _lymphoPctCtrl.dispose();
    _monoAbsCtrl.dispose();
    _monoPctCtrl.dispose();
    _eosAbsCtrl.dispose();
    _eosPctCtrl.dispose();
    _basoAbsCtrl.dispose();
    _basoPctCtrl.dispose();
    _rdwSdCtrl.dispose();
    _rdwCvCtrl.dispose();
    _diseaseTypeCtrl.dispose();
    _subtypeCtrl.dispose();
    _stageCtrl.dispose();
    _statusCtrl.dispose();
    _blastPctCtrl.dispose();
    _boneMarrowCtrl.dispose();
    _chemoCtrl.dispose();
    _notesCtrl.dispose();
    super.dispose();
  }

  double? _parseNum(String text) {
    if (text.trim().isEmpty) return null;
    return double.tryParse(text.trim());
  }

  Future<void> _confirmAndUpdateEhr() async {
    setState(() => _saving = true);

    try {
      final symptomsObj = BloodCancerSymptoms(
        shortnessOfBreath: _symptomsState['shortnessOfBreath'],
        bonePain: _symptomsState['bonePain'],
        fever: _symptomsState['fever'],
        familyHistory: _symptomsState['familyHistory'],
        frequentInfections: _symptomsState['frequentInfections'],
        itchySkinOrRash: _symptomsState['itchySkinOrRash'],
        lossOfAppetiteOrNausea: _symptomsState['lossOfAppetiteOrNausea'],
        persistentWeaknessAndFatigue: _symptomsState['persistentWeaknessAndFatigue'],
        swollenPainlessLymphNodes: _symptomsState['swollenPainlessLymphNodes'],
        significantBruisingOrBleeding: _symptomsState['significantBruisingOrBleeding'],
        enlargedLiver: _symptomsState['enlargedLiver'],
        oralCavityChanges: _symptomsState['oralCavityChanges'],
        visionBlurring: _symptomsState['visionBlurring'],
        jaundice: _symptomsState['jaundice'],
        nightSweats: _symptomsState['nightSweats'],
        smokes: _symptomsState['smokes'],
      );

      final cbcObj = BloodCancerCbc(
        wbc: _parseNum(_wbcCtrl.text),
        rbc: _parseNum(_rbcCtrl.text),
        hemoglobin: _parseNum(_hbCtrl.text),
        hematocrit: _parseNum(_hctCtrl.text),
        platelets: _parseNum(_pltCtrl.text),
        neutrophils: DifferentialCount(
          absolute: _parseNum(_neutroAbsCtrl.text),
          percentage: _parseNum(_neutroPctCtrl.text),
        ),
        lymphocytes: DifferentialCount(
          absolute: _parseNum(_lymphoAbsCtrl.text),
          percentage: _parseNum(_lymphoPctCtrl.text),
        ),
        monocytes: DifferentialCount(
          absolute: _parseNum(_monoAbsCtrl.text),
          percentage: _parseNum(_monoPctCtrl.text),
        ),
        eosinophils: DifferentialCount(
          absolute: _parseNum(_eosAbsCtrl.text),
          percentage: _parseNum(_eosPctCtrl.text),
        ),
        basophils: DifferentialCount(
          absolute: _parseNum(_basoAbsCtrl.text),
          percentage: _parseNum(_basoPctCtrl.text),
        ),
        rdwSd: _parseNum(_rdwSdCtrl.text),
        rdwCv: _parseNum(_rdwCvCtrl.text),
      );

      final updatedEhr = BloodCancerEhrModel(
        recordId: widget.currentEhr?.recordId ?? '',
        patientId: widget.patientId,
        patientName: widget.patientName,
        doctorId: widget.doctorId,
        doctorName: widget.doctorName,
        createdAt: widget.currentEhr?.createdAt ?? DateTime.now(),
        updatedAt: DateTime.now(),
        symptoms: symptomsObj,
        cbc: cbcObj,
        blastCellPercentage: _parseNum(_blastPctCtrl.text),
        diseaseType: _diseaseTypeCtrl.text.trim().isNotEmpty ? _diseaseTypeCtrl.text.trim() : null,
        diagnosisSubtype: _subtypeCtrl.text.trim().isNotEmpty ? _subtypeCtrl.text.trim() : null,
        stage: _stageCtrl.text.trim().isNotEmpty ? _stageCtrl.text.trim() : null,
        diagnosisStatus: _statusCtrl.text.trim().isNotEmpty ? _statusCtrl.text.trim() : null,
        clinicalNotes: _notesCtrl.text.trim().isNotEmpty ? _notesCtrl.text.trim() : null,
        voiceTranscription: widget.extraction.text,
        boneMarrowBiopsy: _boneMarrowCtrl.text.trim().isNotEmpty ? _boneMarrowCtrl.text.trim() : null,
        chemotherapy: _chemoCtrl.text.trim().isNotEmpty ? _chemoCtrl.text.trim() : null,
        medications: widget.currentEhr?.medications ?? const [],
      );

      await _service.saveBloodCancerEhr(updatedEhr);

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('EHR record updated from clinical dictation ✓', style: GoogleFonts.inter(fontSize: 13)),
            backgroundColor: const Color(0xFF1B6B3A),
            behavior: SnackBarBehavior.floating,
          ),
        );
        // Pop back to EHR screen
        Navigator.pop(context); // Pop review screen
        Navigator.pop(context); // Pop voice screen back to EHR screen
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to update EHR: $e', style: GoogleFonts.inter(fontSize: 13)),
            backgroundColor: OV.error,
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: OV.background,
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new_rounded, size: 18, color: OV.onSurface),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text(
          'Review Extracted Clinical Data',
          style: GoogleFonts.manrope(fontSize: 16, fontWeight: FontWeight.w700, color: OV.onSurface),
        ),
      ),
      body: ListView(
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
        children: [
          // ── Header Notice ──────────────────────────────────────
          Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: OV.primaryContainer.withOpacity(0.3),
              borderRadius: BorderRadius.circular(14),
              border: Border.all(color: OV.primary.withOpacity(0.2)),
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Icon(Icons.verified_user_outlined, color: OV.primary, size: 20),
                const SizedBox(width: 10),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('Doctor Verification Required', style: GoogleFonts.manrope(fontSize: 13, fontWeight: FontWeight.w700, color: OV.primary)),
                      const SizedBox(height: 2),
                      Text('Please review the extracted clinical concepts below. You can modify any field before confirming and updating the patient\'s EHR.', style: GoogleFonts.inter(fontSize: 12, color: OV.onSurfaceVariant, height: 1.4)),
                    ],
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 20),

          // ── Original Spoken Dictation ──────────────────────────
          _buildCard(
            title: 'Original Voice Dictation',
            icon: Icons.record_voice_over_outlined,
            child: Text(
              widget.extraction.text.isNotEmpty ? widget.extraction.text : 'No transcript recorded.',
              style: GoogleFonts.inter(fontSize: 13, fontStyle: FontStyle.italic, color: OV.onSurface, height: 1.5),
            ),
          ),

          const SizedBox(height: 16),

          // ── Symptoms Section ───────────────────────────────────
          _buildCard(
            title: 'Extracted Symptoms & Signs',
            icon: Icons.checklist_rounded,
            child: Column(
              children: _symptomLabels.entries.map((entry) {
                final key = entry.key;
                final label = entry.value;
                final state = _symptomsState[key];
                final trace = _symptomsTrace[key];

                return Padding(
                  padding: const EdgeInsets.symmetric(vertical: 6),
                  child: Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: OV.background,
                      borderRadius: BorderRadius.circular(10),
                      border: Border.all(
                        color: state == true
                            ? const Color(0xFF1B6B3A).withOpacity(0.3)
                            : state == false
                                ? OV.error.withOpacity(0.3)
                                : Colors.transparent,
                      ),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Expanded(
                              child: Text(label, style: GoogleFonts.inter(fontSize: 13, fontWeight: FontWeight.w600, color: OV.onSurface)),
                            ),
                            const SizedBox(width: 8),
                            // Segmented Status Choices
                            _statusChip(key, 'Present', true, const Color(0xFF1B6B3A)),
                            const SizedBox(width: 4),
                            _statusChip(key, 'Negated', false, OV.error),
                            const SizedBox(width: 4),
                            _statusChip(key, 'Unstated', null, OV.outline),
                          ],
                        ),
                        if (trace != null && trace.isNotEmpty) ...[
                          const SizedBox(height: 6),
                          Row(
                            children: [
                              const Icon(Icons.format_quote_rounded, size: 14, color: OV.outline),
                              const SizedBox(width: 4),
                              Expanded(
                                child: Text('Matched: "$trace"', style: GoogleFonts.inter(fontSize: 11, fontStyle: FontStyle.italic, color: OV.outline)),
                              ),
                            ],
                          ),
                        ],
                      ],
                    ),
                  ),
                );
              }).toList(),
            ),
          ),

          const SizedBox(height: 16),

          // ── CBC Findings Section ───────────────────────────────
          _buildCard(
            title: 'Complete Blood Count (CBC) Laboratory Findings',
            icon: Icons.science_outlined,
            child: Column(
              children: [
                Row(
                  children: [
                    Expanded(child: _cbcField(_wbcCtrl, 'WBC', 'k/uL', widget.extraction.cbc.wbc?.sourceText)),
                    const SizedBox(width: 10),
                    Expanded(child: _cbcField(_rbcCtrl, 'RBC', 'M/uL', widget.extraction.cbc.rbc?.sourceText)),
                  ],
                ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    Expanded(child: _cbcField(_hbCtrl, 'Hemoglobin', 'g/dL', widget.extraction.cbc.hemoglobin?.sourceText)),
                    const SizedBox(width: 10),
                    Expanded(child: _cbcField(_hctCtrl, 'Hematocrit', '%', widget.extraction.cbc.hematocrit?.sourceText)),
                  ],
                ),
                const SizedBox(height: 12),
                _cbcField(_pltCtrl, 'Platelets', 'k/uL', widget.extraction.cbc.platelets?.sourceText),
                const SizedBox(height: 14),
                const Divider(height: 1),
                const SizedBox(height: 14),
                Text('Differential Leukocyte Counts', style: GoogleFonts.manrope(fontSize: 13, fontWeight: FontWeight.w700, color: OV.onSurface)),
                const SizedBox(height: 10),
                Row(
                  children: [
                    Expanded(child: _cbcField(_neutroAbsCtrl, 'Neutrophils (Abs)', 'k/uL', widget.extraction.cbc.neutrophils?.sourceText)),
                    const SizedBox(width: 10),
                    Expanded(child: _cbcField(_neutroPctCtrl, 'Neutrophils (%)', '%', null)),
                  ],
                ),
                const SizedBox(height: 10),
                Row(
                  children: [
                    Expanded(child: _cbcField(_lymphoAbsCtrl, 'Lymphocytes (Abs)', 'k/uL', widget.extraction.cbc.lymphocytes?.sourceText)),
                    const SizedBox(width: 10),
                    Expanded(child: _cbcField(_lymphoPctCtrl, 'Lymphocytes (%)', '%', null)),
                  ],
                ),
                const SizedBox(height: 10),
                Row(
                  children: [
                    Expanded(child: _cbcField(_monoAbsCtrl, 'Monocytes (Abs)', 'k/uL', widget.extraction.cbc.monocytes?.sourceText)),
                    const SizedBox(width: 10),
                    Expanded(child: _cbcField(_monoPctCtrl, 'Monocytes (%)', '%', null)),
                  ],
                ),
                const SizedBox(height: 10),
                Row(
                  children: [
                    Expanded(child: _cbcField(_eosAbsCtrl, 'Eosinophils (Abs)', 'k/uL', widget.extraction.cbc.eosinophils?.sourceText)),
                    const SizedBox(width: 10),
                    Expanded(child: _cbcField(_eosPctCtrl, 'Eosinophils (%)', '%', null)),
                  ],
                ),
                const SizedBox(height: 10),
                Row(
                  children: [
                    Expanded(child: _cbcField(_basoAbsCtrl, 'Basophils (Abs)', 'k/uL', widget.extraction.cbc.basophils?.sourceText)),
                    const SizedBox(width: 10),
                    Expanded(child: _cbcField(_basoPctCtrl, 'Basophils (%)', '%', null)),
                  ],
                ),
                const SizedBox(height: 14),
                const Divider(height: 1),
                const SizedBox(height: 14),
                Row(
                  children: [
                    Expanded(child: _cbcField(_rdwSdCtrl, 'RDW-SD', 'fL', widget.extraction.cbc.rdwSd?.sourceText)),
                    const SizedBox(width: 10),
                    Expanded(child: _cbcField(_rdwCvCtrl, 'RDW-CV', '%', widget.extraction.cbc.rdwCv?.sourceText)),
                  ],
                ),
              ],
            ),
          ),

          const SizedBox(height: 16),

          // ── Staging & Regimen Section ──────────────────────────
          _buildCard(
            title: 'Diagnosis, Staging & Clinical Notes',
            icon: Icons.biotech_rounded,
            child: Column(
              children: [
                _inputField(_diseaseTypeCtrl, 'Disease Type', 'e.g. Acute Leukemia, Chronic Leukemia'),
                const SizedBox(height: 10),
                _inputField(_subtypeCtrl, 'Diagnosis Subtype', 'e.g. AML, ALL, CML, CLL'),
                const SizedBox(height: 10),
                Row(
                  children: [
                    Expanded(child: _inputField(_stageCtrl, 'Stage / Risk Level', 'e.g. Intermediate, Stage II')),
                    const SizedBox(width: 10),
                    Expanded(child: _inputField(_statusCtrl, 'Diagnosis Status', 'e.g. Active, In Remission')),
                  ],
                ),
                const SizedBox(height: 10),
                _inputField(_blastPctCtrl, 'Blast Cell Percentage (%)', 'e.g. 1.5'),
                const SizedBox(height: 10),
                _inputField(_chemoCtrl, 'Chemotherapy Regimen', 'e.g. 7+3 Induction, HiDAC'),
                const SizedBox(height: 10),
                _inputField(_boneMarrowCtrl, 'Bone Marrow Biopsy / Remarks', 'Biopsy findings and cytogenetics...'),
                const SizedBox(height: 10),
                _inputField(_notesCtrl, 'Clinical Impressions & Directives', 'Document treatment response...', maxLines: 4),
              ],
            ),
          ),

          const SizedBox(height: 24),

          // ── Confirm Button ─────────────────────────────────────
          ElevatedButton.icon(
            onPressed: _saving ? null : _confirmAndUpdateEhr,
            icon: _saving
                ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                : const Icon(Icons.check_circle_outline_rounded, size: 20),
            label: Text(
              _saving ? 'Saving to EHR...' : 'Confirm & Update EHR',
              style: GoogleFonts.manrope(fontSize: 14, fontWeight: FontWeight.w700),
            ),
            style: ElevatedButton.styleFrom(
              backgroundColor: OV.slateDark,
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(vertical: 16),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
              elevation: 0,
            ),
          ),

          const SizedBox(height: 30),
        ],
      ),
    );
  }

  Widget _statusChip(String key, String label, bool? targetVal, Color activeColor) {
    final currentVal = _symptomsState[key];
    final isSelected = currentVal == targetVal;

    return InkWell(
      onTap: () {
        setState(() => _symptomsState[key] = targetVal);
      },
      borderRadius: BorderRadius.circular(6),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
        decoration: BoxDecoration(
          color: isSelected ? activeColor : Colors.white,
          borderRadius: BorderRadius.circular(6),
          border: Border.all(
            color: isSelected ? activeColor : OV.outlineVariant.withOpacity(0.5),
          ),
        ),
        child: Text(
          label,
          style: GoogleFonts.inter(
            fontSize: 11,
            fontWeight: isSelected ? FontWeight.w700 : FontWeight.w500,
            color: isSelected ? Colors.white : OV.onSurfaceVariant,
          ),
        ),
      ),
    );
  }

  Widget _cbcField(TextEditingController ctrl, String label, String unit, String? source) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(label, style: GoogleFonts.inter(fontSize: 12, fontWeight: FontWeight.w600, color: OV.onSurface)),
            Text(unit, style: GoogleFonts.inter(fontSize: 11, color: OV.outline)),
          ],
        ),
        const SizedBox(height: 4),
        TextField(
          controller: ctrl,
          keyboardType: const TextInputType.numberWithOptions(decimal: true),
          style: GoogleFonts.inter(fontSize: 13, color: OV.onSurface),
          decoration: InputDecoration(
            isDense: true,
            contentPadding: const EdgeInsets.symmetric(horizontal: 10, vertical: 10),
            border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
          ),
        ),
        if (source != null && source.isNotEmpty) ...[
          const SizedBox(height: 2),
          Text('"$source"', maxLines: 1, overflow: TextOverflow.ellipsis, style: GoogleFonts.inter(fontSize: 10, fontStyle: FontStyle.italic, color: OV.outline)),
        ],
      ],
    );
  }

  Widget _inputField(TextEditingController ctrl, String label, String hint, {int maxLines = 1}) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: GoogleFonts.inter(fontSize: 12, fontWeight: FontWeight.w600, color: OV.onSurface)),
        const SizedBox(height: 4),
        TextField(
          controller: ctrl,
          maxLines: maxLines,
          style: GoogleFonts.inter(fontSize: 13, color: OV.onSurface),
          decoration: InputDecoration(
            isDense: true,
            hintText: hint,
            hintStyle: GoogleFonts.inter(fontSize: 12, color: OV.outlineVariant),
            contentPadding: const EdgeInsets.symmetric(horizontal: 10, vertical: 10),
            border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
          ),
        ),
      ],
    );
  }

  Widget _buildCard({required String title, required IconData icon, required Widget child}) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: OV.outlineVariant.withOpacity(0.5)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, size: 18, color: OV.primary),
              const SizedBox(width: 8),
              Expanded(
                child: Text(title, style: GoogleFonts.manrope(fontSize: 14, fontWeight: FontWeight.w700, color: OV.onSurface)),
              ),
            ],
          ),
          const SizedBox(height: 14),
          child,
        ],
      ),
    );
  }
}
