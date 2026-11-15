import json,pathlib,tempfile,unittest
import worker
from categories import classify_result

class SummaryTests(unittest.TestCase):
    def test_all_mismatches_counted_but_samples_bounded(self):
        with tempfile.TemporaryDirectory() as temporary:
            path=pathlib.Path(temporary)/'report.json'
            path.write_text(json.dumps({'archive_accepted':False,'native_frames':61,'replayed_frames':61,
                'mismatches':[{'field':'command_query_event','native':{'args':[1,None,3]},'deadsync':{'args':[2,None,3]}} for _ in range(53)],
                'errors':['callback failed'],'pending_coverage':[{'field':'drawable','reason':'not sampled'}]}))
            result=worker.document_summary(path,report=True)
            self.assertEqual(result['mismatch_count'],53)
            self.assertEqual(result['mismatch_fields'],{'command_query_event':53})
            self.assertEqual(len(result['first_mismatches']),40)
            self.assertEqual(result['errors'],['callback failed'])
            self.assertEqual(result['pending_coverage'][0]['field'],'drawable')
    def test_native_metadata_keeps_source_and_completion(self):
        with tempfile.TemporaryDirectory() as temporary:
            path=pathlib.Path(temporary)/'native.json'
            path.write_text(json.dumps({'schema_version':1,'input':{'native_source':{'revision':'abc','modified_src':False}},
                'events':[{'kind':'error','detail':{'message':'bad source'}}],
                'completion':{'reason':'gameplay-exit'},'dropped_events':4}))
            result=worker.document_summary(path)
            self.assertEqual(result['input']['native_source']['revision'],'abc')
            self.assertEqual(result['completion']['reason'],'gameplay-exit')
            self.assertEqual(result['dropped_events'],4)
            self.assertNotIn('events',result)
            self.assertEqual(worker.native_errors(path)[0]['detail']['message'],'bad source')
    def test_resource_failures_are_not_parity_failures(self):
        self.assertEqual(worker.failure_category('capture',{'service_tail':'Result: oom-kill'},''),'capture_resource_limit')
        self.assertEqual(worker.failure_category('capture',{},'ITGmania did not write a semantic trace within 900 seconds'),'capture_timeout')
        self.assertEqual(worker.failure_category('capture',{},'no StepsType_Dance_Single chart matched difficulty Challenge'),'no_selectable_chart')
        self.assertEqual(worker.failure_category('capture',{'service_tail':'Started capture --timeout 900'},'native gameplay capture contains errors or dropped observations'),'native_capture_error')
        self.assertEqual(worker.failure_category('capture',{'service_tail':'Started capture --timeout 900'},'ITGmania exited with signal: 9 (SIGKILL) before writing a semantic trace'),'native_process_exit')
    def test_crash_hidden_by_timeout_keeps_debugger_evidence(self):
        result={'status':'capture_timeout','stages':{'capture':{'exit':1}},
          'reason':'ITGmania did not write a semantic trace within 900 seconds',
          'native_hang_debugger':'__libc_fork RunCrashHandler malloc_printerr'}
        self.assertEqual(classify_result(result)['status'],'native_crash_handler_hang')
    def test_analysis_matches_array_tolerance_and_exact_object_equality(self):
        import importlib.util
        spec=importlib.util.spec_from_file_location('analysis',pathlib.Path(__file__).with_name('analyze-reports.py'))
        analysis=importlib.util.module_from_spec(spec);spec.loader.exec_module(analysis)
        self.assertTrue(analysis.same([1.0,2.0],[1.0000001,2]))
        self.assertFalse(analysis.same([{'value':1.0}],[{'value':1.0000001}]))
        self.assertFalse(analysis.same([{'value':1}],[{'value':1.0}]))
        self.assertFalse(analysis.same(True,1))

if __name__=='__main__':unittest.main()
